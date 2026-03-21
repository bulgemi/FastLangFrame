import json
import logging
import sys
import uuid
from contextvars import ContextVar, copy_context
from functools import partial
from itertools import chain
from typing import Annotated, Any, Literal, Type

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup

import inspect
import traceback
from functools import wraps
from types import TracebackType
from typing import Callable

from fastapi import Header, Request
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    WebSocketException,
    WebSocketRequestValidationError,
)
from langchain_core.tracers.schemas import Run
from openinference.instrumentation import (
    OITracer,
    dangerously_using_project,
    get_attributes_from_context,
    using_attributes,
)
from openinference.instrumentation.helpers import get_span_id, get_trace_id
from openinference.instrumentation.langchain._tracer import (
    _as_input,
    _as_output,
    _convert_io,
    _flatten,
    _function_calls,
    _input_messages,
    _invocation_parameters,
    _metadata,
    _model_name,
    _output_messages,
    _prompt_template,
    _prompts,
    _retrieval_documents,
    _token_counts,
    _tools,
)
from opentelemetry import context as context_api
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# from opentelemetry.trace import get_tracer, get_tracer_provider, set_tracer_provider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.trace import Span
from opentelemetry.sdk.trace import TracerProvider as OTelTracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace.span import NonRecordingSpan
from phoenix.otel import TracerProvider as PhoenixTracerProvider
from phoenix.otel import register
from pydantic import BaseModel, field_validator
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from starlette.types import Message, Receive, Scope, Send
from typing_extensions import Self

from mari_agent.common.config import phoenix_config


def gen_session_id(session_id: str | None):
    return session_id or str(uuid.uuid4())


def build_tags(values: dict[str, str]) -> set[str]:
    return set(f"{k}:{v}" for k, v in values if v is not None)


TraceEngine = Literal["langchain", "langgraph", "openai", "autogen"]
FeedbackType = Literal["thumbsup", "score"]


def get_instrument(engine: TraceEngine = "langgraph") -> BaseInstrumentor:
    match engine:
        case "langchain" | "langgraph":
            from openinference.instrumentation.langchain import LangChainInstrumentor

            return LangChainInstrumentor

        case _:
            raise TypeError(f"'engine' should be one of {TraceEngine}")


def get_span_exporter(tracer_provider: PhoenixTracerProvider):
    active_span_processsor = tracer_provider._active_span_processor
    span_processors = active_span_processsor._span_processors
    span_processor = span_processors[0]
    span_exporter = span_processor.span_exporter
    span_exporter._headers

    # from httpx import URL, _urlparse

    # span_exporter._endpoint
    # url = URL(span_exporter._endpoint)
    return span_exporter


def get_tracer(
    project_name: str = "default",
    endpoint: str | None = None,
    verbose: bool | None = None,
    batch: bool = False,
    as_global: bool = False,
) -> PhoenixTracerProvider:
    return register(
        endpoint=endpoint or phoenix_config.endpoint,
        project_name=project_name,
        set_global_tracer_provider=as_global,
        batch=batch,
        verbose=verbose or phoenix_config.verbose,
        auto_instrument=True,
    )


GLOBAL_TRACER_PROVIDER = ContextVar("GLOBAL_TRACER_PROVIDER")  # PhoenixTracerProvider
GLOBAL_TRACERS = ContextVar("GLOBAL_TRACERS")  # list[OITracer]
GLOBAL_TRACERS.set({})
GLOBAL_ROOT_TRACER = ContextVar("GLOBAL_ROOT_TRACER")  # OITracer
GLOBAL_TRACER_ENABLED = ContextVar("GLOBAL_TRACER_ENABLED")  # bool: False
GLOBAL_TRACER_ENABLED.set(False)


def _get_project_name_from_tracer_provider(
    tracer_provider: PhoenixTracerProvider,
) -> str | None:
    return tracer_provider.resource.attributes.get("openinference.project.name")


class using_tracer:
    def __init__(
        self,
        tracer_provider: PhoenixTracerProvider | None = None,
        engines: TraceEngine = ["langgraph"],
        project_name: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] = None,
        tags: list[str] | None = None,
        prompt_template: str = "",
        prompt_template_variables: dict[str, str] | None = None,
        prompt_template_version: str = "",
        enable: bool = True,
    ):
        self.tracing_enabled = enable or phoenix_config.enabled
        GLOBAL_TRACER_ENABLED.set(self.tracing_enabled)

        if self.tracing_enabled:
            self.verbose = phoenix_config.verbose

            self.tracer_provider: PhoenixTracerProvider | OTelTracerProvider
            if tracer_provider:
                self.tracer_provider = tracer_provider
            else:
                self.tracer_provider = get_tracer(project_name=project_name)
                self.tracer_provider.add_span_processor(
                    SimpleSpanProcessor(
                        OTLPSpanExporter(
                            phoenix_config.endpoint,
                            headers=(
                                {
                                    "authorization": f"Bearer {phoenix_config.phoenix_apikey}"
                                }
                                if phoenix_config.phoenix_apikey
                                else None
                            ),
                        ),
                    )
                )
                if phoenix_config.verbose:
                    # verbose가 true여야 console에 logging
                    self.tracer_provider.add_span_processor(
                        SimpleSpanProcessor(ConsoleSpanExporter())
                    )

            GLOBAL_TRACER_PROVIDER.set(self.tracer_provider)
            self.project_name = project_name or _get_project_name_from_tracer_provider(
                self.tracer_provider
            )

            self.engines = engines
            self.instruments = []
            self.tracers = {}
            for engine in engines:
                instrument_cls = get_instrument(engine)
                # instrument: openinference.instrumentation.langchain.LangChainInstrumentor
                instrument = instrument_cls()
                instrument.instrument(tracer_provider=self.tracer_provider)
                self.instruments.append(instrument)
                self.tracers[engine] = getattr(instrument, "_tracer")

            GLOBAL_TRACERS.set(self.tracers)
            self.main_tracer: OITracer = self.tracer_provider.get_tracer("RootTracer")
            GLOBAL_ROOT_TRACER.set(self.main_tracer)
            self.span_exporter = get_span_exporter(self.tracer_provider)

            self.session_id = gen_session_id(session_id)
            self.user_id = user_id or ""
            self.metadata = metadata
            self.tags = tags

            self.prompt_template = prompt_template
            self.prompt_template_variables = prompt_template_variables
            self.prompt_template_version = prompt_template_version

            self._using_project = dangerously_using_project(self.project_name)
            self._using_tracer_attributes = using_attributes(
                session_id=self.session_id,
                user_id=self.user_id,
                metadata=self.metadata,
                tags=self.tags,
                prompt_template=self.prompt_template,
                prompt_template_variables=self.prompt_template_variables,
                prompt_template_version=self.prompt_template_version,
            )
            self.span = self.main_tracer.start_span(
                "User Agent",
                openinference_span_kind="agent",
            )
            # self._using_langchain_runs_cb = langchain_context.collect_runs() #langchain callback handler. 없어도 chain 잘 잡아서 주석처리함
            self.input: dict[str, str] = {}
            self.output: dict[str, str] = {}
            self.span_id = None
            self.trace_id = None

    def __enter__(self) -> Self:
        if self.tracing_enabled:
            self._using_project.__enter__()
            self._using_tracer_attributes.__enter__()
            # self.langchain_runs = self._using_langchain_runs_cb.__enter__()

        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if self.tracing_enabled:
            # self._using_langchain_runs_cb.__exit__(exc_type, exc_val, exc_tb)
            self._using_tracer_attributes.__exit__(exc_type, exc_val, exc_tb)
            self._using_project.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> Self:
        self.__enter__()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)

    def add_input(self, input_: dict[str, str] | str):
        self.input = input_
        self.span.set_attributes(
            dict(
                _flatten(
                    chain(
                        _as_input(_convert_io(input_)),
                        _prompts(input_),
                        _input_messages(input_),
                    )
                )
            )
        )

    def add_output(self, output_: dict[str, str] | str):
        self.span.set_attributes(
            dict(
                _flatten(
                    chain(
                        _as_output(_convert_io(output_)),
                        _output_messages(output_),
                    )
                )
            )
        )

    def set_span_attributes(
        self,
        prompt_template,
        metadata,
    ):
        self.span.set_attributes(
            dict(
                _flatten(
                    chain(
                        _prompt_template(prompt_template),
                        _metadata(metadata),
                    )
                )
            )
        )

    def _set_langchain_span_attributes(self, run: Run):
        inputs = self.input or run.inputs
        output = self.output or run.outputs
        self.span.set_attributes(dict(get_attributes_from_context()))
        self.span.set_attributes(
            dict(
                _flatten(
                    chain(
                        _as_input(_convert_io(inputs)),
                        _as_output(_convert_io(output)),
                        _prompts(inputs),
                        _input_messages(inputs),
                        _output_messages(output),
                        _prompt_template(run),
                        _invocation_parameters(run),
                        _model_name(run.extra),
                        _token_counts(output),
                        _function_calls(output),
                        _tools(run),
                        _retrieval_documents(run),
                        _metadata(run),
                    )
                )
            )
        )

    def add_feedback(
        self,
        feedback_name: str = "feedback",
        type: FeedbackType = "thumsup",
        thumbsup: bool = True,
        score: float = 1.0,
        explanation: str = "",
        metadata: dict[str, str] = {},
        headers: dict[str, str] = None,
    ):
        span_id = get_span_id(self.span)
        trace_id = get_trace_id(self.span)
        if not self.span_id:
            raise ValueError("span has not been created.")
        else:
            add_feedback(
                span_id=self.span_id,
                feedback_name=feedback_name,
                type=type,
                thumbsup=thumbsup,
                score=score,
                explanation=explanation,
                metadata=metadata or self.metadata,
                # headers=headers,
            )


def add_feedback(
    span_id: str,
    feedback_name: str = "feedback",
    type: FeedbackType = "thumsup",
    thumbsup: bool = True,
    score: float = 1.0,
    explanation: str = "",
    metadata: dict[str, str] = {},
    headers: dict[str, str] = None,
):
    import httpx

    kind: str = "HUMAN"
    name: str = "feedback"

    value: dict[str, str | float]
    if type == "thumbsup":
        value = {
            "label": "thumbsup",
            "score": float(thumbsup),
            "explanation": explanation,
        }
    elif type == "score":
        value = {
            "label": "score",
            "score": score,
            "explanation": explanation,
        }

    with httpx.Client() as client:
        from httpx import URL

        annotation_payload = {
            "data": [
                {
                    "span_id": span_id,
                    "name": name,
                    "annotator_kind": kind,
                    "result": value,
                    "metadata": metadata,
                }
            ]
        }

        # headers = {"api_key": "<your phoenix api key>"}
        url = URL(phoenix_config.endpoint)
        host = f"{url.scheme}://{url.netloc.decode()}"

        resp = client.post(
            f"{host}/v1/span_annotations?sync=false",
            json=annotation_payload,
            headers=headers,
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            resp.raise_for_status()


class TraceHeaders(BaseModel):
    model_config = {"extra": "allow"}

    session_id: str | None
    user_id: str | None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None

    @field_validator("tags", mode="before")
    def get_unique_tags(cls, v):
        if v and len(v) > 0:
            tags_str = v[0]
            tags = set(tags_str.split(","))
            return list(tags)
        else:
            return []

    @field_validator("metadata", mode="before")
    def get_metadata(cls, v):
        if v and isinstance(v, str):
            metadata = json.dumps(str)
            return metadata
        else:
            return {}


TraceHeadersAnnotated = Annotated[TraceHeaders, Header()]


def as_header(cls):
    """decorator for pydantic model
    replaces the Signature of the parameters of the pydantic model with `Header`

    Example:
    >>> from pydantic import BaseModel
    >>> from fastapi import FastAPI, Request, Depends
    >>> @as_header
    ... clss APIInfo(BaseModel):
    ...     key_a: str
    ...     key_b: str

    >>> def additional_key_headers(
    ...     request: Request, api_info: APIInfo = Depends(APIInfo)
    ... ):
    ...     request.api_info = api_info

    >>> app = FastAPI(dependencies=[Depends(additional_key_headers)])

    >>> @app.get("/")
    ... def get_api_version_info(request: Request):
    ...     return request.api_info
    """
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(
                default=Header(...) if arg.default is arg.empty else Header(arg.default)
            )
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


def traced(
    func: Callable,
    engines: TraceEngine = ["langgraph"],
    name: str | None = None,
):
    """Add a tracer to a decorated class or function.

    Args:
        obj (Callable)

    Example:
        >>> @traced
        ... class CallableObject:
        ...     def __call__(self, a: int) -> int:
        ...         return a

        >>> @traced
        ... def func(a: int) -> int:
        ...     return a
    """

    if not (inspect.ismethod(func) or callable(func)):
        return func

    @wraps(func)
    def traced_decorator(*args, **kwargs):
        func_sig = inspect.signature(func)
        func_accepts_parent_run = func_sig.parameters.get("run_tree", None) is not None
        func_accepts_config = func_sig.parameters.get("config", None) is not None
        try:
            ctx = copy_context()

            if not ctx.get(GLOBAL_TRACER_ENABLED):
                return func(*args, **kwargs)

            global_tracers: dict[str, OITracer] = ctx.get(GLOBAL_TRACERS)
            global_root_tracer: OITracer = ctx.get(GLOBAL_ROOT_TRACER)
            if global_root_tracer is None:
                tracer_provider = get_tracer(project_name="default")
                tracer_provider.add_span_processor(
                    SimpleSpanProcessor(OTLPSpanExporter(phoenix_config.endpoint))
                )
                tracer_provider.add_span_processor(
                    SimpleSpanProcessor(ConsoleSpanExporter())
                )
                global_root_tracer = tracer_provider.get_tracer("RootTracer")

            _self_obj = args[0]
            obj_name = getattr(_self_obj, "name", None)
            obj_id = getattr(_self_obj, "id", None)
            if obj_id:
                raw_span_name = obj_id
                span_name = obj_name
            else:
                span_name = name or func.__qualname__

            from openinference.instrumentation.langchain._tracer import (
                OpenInferenceTracer,
            )

            langgraph_tracer: OpenInferenceTracer = global_tracers.get("langgraph")

            langchain_spans_items = [
                (k, v) for k, v in langgraph_tracer._spans_by_run.items()
            ]

            parent_span = None
            child_span = None
            if langchain_spans_items:
                if len(langchain_spans_items) != 2:
                    pass
                for _span_key, _span in langgraph_tracer._spans_by_run.items():
                    if _span.parent is None:
                        parent_span = _span
                    else:
                        child_span = _span

            current_context = context_api.get_current()

            current_span: Span = child_span or trace_api.get_current_span()
            if isinstance(current_span, NonRecordingSpan):
                with global_root_tracer.start_as_current_span(
                    span_name,
                    context=current_context,
                    openinference_span_kind="chain",
                ) as new_span:
                    return func(*args, **kwargs)
            else:
                current_span.update_name(f"{span_name}__[{current_span.name}]")
                with trace_api.use_span(current_span):
                    return func(*args, **kwargs)
        except Exception as e:
            _log_exception(e, logging.getLogger(__name__))
            return func(*args, **kwargs)

    return traced_decorator


async def using_tracer_as_fastapi_dependency(
    request: Request,
):
    user_id = request.headers.get("aip-user", None)
    project_name = (
        request.headers.get("aip-project", None) or phoenix_config.project_name
    )

    tracer = using_tracer(
        project_name=project_name,
        user_id=user_id,
        metadata={},
        tags=None,
        enable=phoenix_config.enabled,
    ).__enter__()
    try:
        yield tracer
    except Exception as e:
        tracer.__exit__(exc_type=type(e), exc_val=e, exc_tb=e.__traceback__)
    finally:
        tracer.__exit__(exc_type=None, exc_val=None, exc_tb=None)


_json_dumps = partial(json.dumps, indent=4, sort_keys=True, ensure_ascii=False)


def _get_request_info(request: Request, body: bytes | None = None) -> str:
    body_msg: str = ""
    try:
        if not body or body is None:
            body_msg = _json_dumps(body)
        elif isinstance(body, bytes):
            try:
                body_msg = _json_dumps(json.loads(body.decode()) or None)
            except json.JSONDecodeError:
                body_msg = str(body)
        elif isinstance(body, dict):
            body_msg = _json_dumps(body)
        else:
            body_msg = str(body)
    except Exception:
        body_msg = str(body)

    return "\n".join(
        [
            "=" * 50,
            "<Request>",
            f"client: {request.client}",
            f"method: {request.method}",
            f"url: {request.url}",
            f"headers: \n{_json_dumps(dict(request.headers))}",
            f"body: \n{body_msg}",
            "=" * 50,
        ],
    )


def _get_last_traceback(tb: TracebackType) -> TracebackType:
    """Get last traceback"""
    new_tb = tb.tb_next
    if new_tb is None:
        return tb
    return _get_last_traceback(new_tb)


def _gen_logtrace_id() -> str:
    """Generate random trace id"""
    return f"log-{uuid.uuid4()!s}"


class TracerException(HTTPException):
    """Application-managed Exception, which is an exception wrapper.

    This Exception is designed to handle the exceptions raised from
    application API is responsing. When it is raised, it is catched by
    exception handlers and `ErrorResponse` is responsed.


    Parameters
    ----------
    e: Exception
        An system raised exception to wrap.

    msg: str | None (default: None)
        optionally, message appended

    status_code: int | None (default: None)

    Examples
    --------
    #>>> import requests
    #>>> from .types.exceptions import TracerException
    #>>> try:
    #...     r = requests.get("https://google.com")
    #... except Exception as e:
    #...     raise TracerException(e=e)

    """

    trace_id: str
    system_message: str | None = None
    system_stack_trace: str | None = None

    def __init__(
        self,
        e: Exception | None = None,
        msg: str | None = None,
        status_code: int | None = None,
    ) -> None:
        delimiter = ": "
        self.message = msg or ""
        self.trace_id = _gen_logtrace_id()

        if e is None:
            self.system_message = self.message
            exc_type = type(self)
            self.system_stack_trace = delimiter.join(
                [
                    f"{{ErrorType: {exc_type}}}",
                ],
            )
        else:
            tb = e.__traceback__
            last_tb = _get_last_traceback(tb)
            exc_type = e.__class__.__name__
            filename = last_tb.tb_frame.f_code.co_filename
            name = last_tb.tb_frame.f_code.co_name
            line = last_tb.tb_lineno
            stack = "".join(traceback.format_tb(e.__traceback__))
            exc_msg = f"{exc_type}: {e!s}"
            self.system_message = f"{self.message}: {exc_msg}"
            self.system_stack_trace = "\n".join(
                [
                    f"ErrorType: {exc_type}",
                    f"File: {filename}",
                    f"Name: {name}",
                    f"Line: {line}",
                    f"Traceback: \n{stack}{exc_msg}",
                ],
            )

        if status_code:
            super(HTTPException, self).__init__(
                status_code=status_code,
                detail=self.message,
            )

        elif isinstance(e, (HTTPException, WebSocketException)):
            super().__init__(status_code=e.status_code, detail=self.message)
        elif isinstance(e, (RequestValidationError, WebSocketRequestValidationError)):
            super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=self.message)
        else:
            super().__init__(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=self.message,
            )

    @property
    def log_message(self) -> str:
        """Log message"""
        return "\n" + "\n".join(
            [
                "=" * 50,
                f"TraceID: {self.trace_id}",
                f"SYSMSG: {self.system_message}",
                "=" * 50,
                f"StackTrace: \n{self.system_stack_trace}",
            ],
        )


def _log_exception(exc: Exception, logger: logging.Logger, request_msg: str = ""):
    if isinstance(exc, TracerException):
        logger.error(f"{request_msg}\n{exc.log_message}")
    else:
        wrapped_exc = TracerException(e=exc)
        logger.error(f"{request_msg}\n{wrapped_exc.log_message}")


class TraceExceptionMiddleware(ExceptionMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__log = logging.getLogger(self.__class__.__qualname__)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        request = Request(scope)
        try:
            user_id = request.headers.get("aip-user", None)
            project_name = (
                request.headers.get("aip-project", None) or phoenix_config.project_name
            )

            with using_tracer(
                project_name=project_name,
                user_id=user_id,
                metadata={},
                tags=None,
                enable=phoenix_config.enabled,
            ) as tracer:
                await self.app(scope, receive, sender)
        except Exception as exc:
            # This handles the exceptions from background_tasks which is already responsed.
            # Case message is "RuntimeError: Caught handled exception, but response already started."
            request = Request(scope)
            request_msg = _get_request_info(request)

            if isinstance(exc, ExceptionGroup):
                for real_exc in exc.exceptions:
                    _log_exception(real_exc, self.__log, request_msg=request_msg)
            else:
                real_exc = exc.__cause__
                if real_exc:
                    _log_exception(real_exc, self.__log, request_msg=request_msg)
                else:
                    _log_exception(exc, self.__log, request_msg=request_msg)
