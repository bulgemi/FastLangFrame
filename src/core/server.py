import jwt
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    OAuth2AuthorizationCodeBearer,
)

from .api_models import (
    AgentInvokeRequest,
    AgentBatchRequest,
    AgentInvokeResponse,
    AgentBatchResponse,
)
from src.common.middleware.auth import (
    verify_token,
    verify_authelia_token,
    create_access_token,
)
from src.common.configs.settings import get_settings
from src.common.logging.logger_config import setup_logger
from src.utils.connectors.db.database import db

settings = get_settings()
logger = setup_logger(__name__)


async def get_current_verify_token():
    """Dynamic dependency to select the verification method based on settings."""
    # Preference: Local Authelia Validation > Introspection > Native Token
    if settings.authelia_url:
        return verify_authelia_token
    return verify_token


# Global schemes to be used as dependencies
# We use a factory function to ensure they are created with current settings but reused by FastAPI
_password_scheme = None
_oauth2_scheme = None


def get_password_scheme():
    global _password_scheme
    if _password_scheme is None:
        _password_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
    return _password_scheme


def get_oauth2_scheme():
    global _oauth2_scheme
    if _oauth2_scheme is None:
        _oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=settings.authelia_authorization_url or "",
            tokenUrl=settings.authelia_token_url or "",
            scopes={
                "openid": "OpenID Connect",
                "profile": "User Profile",
                "email": "User Email",
            },
            auto_error=False,
            scheme_name="OAuth2",
        )
    return _oauth2_scheme


async def authenticated_user(
    token_password: Optional[str] = Depends(get_password_scheme()),
    token_oauth2: Optional[str] = Depends(get_oauth2_scheme()),
):
    """
    Unified authentication dependency.
    """
    token = token_oauth2 or token_password

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")

        if alg == "RS256":
            # Authelia / OIDC token
            return await verify_authelia_token(token)
        elif alg == "HS256":
            # Native JWT token
            return await verify_token(token)
        else:
            # Fallback or unrecognized algorithm
            verify_func = await get_current_verify_token()
            return await verify_func(token)
    except Exception as e:
        logger.error(f"Token header analysis failed: {str(e)}")
        # If header parsing fails, try the default configured method
        verify_func = await get_current_verify_token()
        return await verify_func(token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB Engine
    logger.info("Initializing database engine...")
    try:
        # Accessing async_engine triggers initialization in our lazy-loading Database class
        _ = db.async_engine
        logger.info("Database engine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")

    yield
    # Shutdown: Close DB connections if needed (SQLAlchemy handles most of this via pooling)
    logger.info("Shutting down database engine...")


def agent_json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for LangGraph and LangChain objects.
    Ensures that types like 'Overwrite' and 'BaseMessage' are serializable.
    """
    # 1. LangGraph Overwrite handling (common in deepagent updates)
    if obj.__class__.__name__ == "Overwrite" and hasattr(obj, "value"):
        return obj.value

    # 2. LangChain BaseMessage and Pydantic models
    if hasattr(obj, "dict") and callable(obj.dict):
        return obj.dict()

    # 3. Fallback to string representation
    try:
        return str(obj)
    except Exception:
        return f"<Non-serializable {type(obj).__name__}>"


def create_agent_app(graph: Any, title: str = "FastLangFrame API Server") -> FastAPI:
    """
    LangGraph 객체(또는 Runnable)를 받아 /invoke, /stream, /invoke_batch, /invoke_stream_batch
    엔드포인트가 장착된 FastAPI 앱을 생성하여 반환합니다.
    """
    app = FastAPI(
        title=title,
        lifespan=lifespan,
        swagger_ui_init_oauth={
            "clientId": settings.authelia_client_id,
            "appName": title,
            "usePkceWithAuthorizationCodeGrant": True,
            "scopes": "openid profile email",
        },
    )

    @app.post("/token", summary="Token 발행")
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        """사용자 이름과 비밀번호를 받아 JWT를 발급합니다."""
        # 1. Fallback (개발/테스트용): 간단한 검증
        if form_data.username == "testuser" and form_data.password == "testpassword":
            user_info = {"sub": "testuser", "name": "Test User", "groups": ["admins"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Native JWT 생성
        access_token = create_access_token(data=user_info)
        return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/api/v1/auth/callback", summary="Authelia Callback")
    async def authelia_callback(code: str):
        """
        OIDC callback endpoint that receives the authorization code
        and exchanges it for a token from Authelia.
        """
        token_data = await exchange_code_for_authelia_token(code)
        # For simplicity, we just return the token data from Authelia.
        # In a real app, you might want to issue a native JWT or set a session cookie.
        return token_data

    @app.get("/", summary="Health Check")
    async def root():
        return {"status": "ok", "message": f"Welcome to {title}"}

    @app.post("/invoke", summary="Agent 실행", response_model=AgentInvokeResponse)
    async def invoke(req: AgentInvokeRequest, auth: dict = Depends(authenticated_user)):
        """단일 Agent 입력을 받아 전체 처리가 끝난 뒤 결과 반환"""
        try:
            result = await graph.ainvoke(req.input, req.config)
            # BaseMessage 등 직렬화 불가능한 객체 처리 (필요시)
            return AgentInvokeResponse(result=result)
        except Exception as e:
            return AgentInvokeResponse(error=str(e), status="error")

    @app.post("/stream", summary="Agent 스트리밍 실행")
    async def stream(req: AgentInvokeRequest, auth: dict = Depends(authenticated_user)):
        """단일 Agent 실행 중 이벤트를 SSE 스트림으로 반환"""

        async def event_generator():
            try:
                async for event in graph.astream(req.input, req.config):
                    yield f"data: {json.dumps(event, default=agent_json_serializer)}\n\n"
                yield f"data: {json.dumps({'__end__': True}, default=agent_json_serializer)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, default=agent_json_serializer)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.post(
        "/invoke_batch", summary="Agent 배치 실행", response_model=AgentBatchResponse
    )
    async def invoke_batch(
        req: AgentBatchRequest, auth: dict = Depends(authenticated_user)
    ):
        """다수의 입력을 병렬로 처리 후 모든 결과가 완료되면 리스트 리턴"""
        try:
            results = await graph.abatch(req.inputs, req.config)
            return AgentBatchResponse(results=results)
        except Exception as e:
            return AgentBatchResponse(error=str(e), status="error")

    @app.post("/invoke_stream_batch", summary="Agent 스트리밍 배치 실행")
    async def invoke_stream_batch(
        req: AgentBatchRequest, auth: dict = Depends(authenticated_user)
    ):
        """
        다중 배치를 동시에 시작하여 각 입력별 스트림 이벤트를
        하나의 SSE 스트림으로 병합(Interleaved) 전송합니다.
        """

        async def event_generator():
            queue = asyncio.Queue()

            async def stream_item(index: int, inp: dict):
                try:
                    async for event in graph.astream(inp, req.config):
                        await queue.put({"index": index, "event": event})
                except Exception as e:
                    await queue.put({"index": index, "error": str(e)})
                finally:
                    await queue.put({"index": index, "done": True})

            tasks = [
                asyncio.create_task(stream_item(i, inp))
                for i, inp in enumerate(req.inputs)
            ]

            active_tasks = len(tasks)
            while active_tasks > 0:
                item = await queue.get()
                if item.get("done"):
                    active_tasks -= 1
                yield f"data: {json.dumps(item, default=agent_json_serializer)}\n\n"

            for t in tasks:
                t.cancel()

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app
