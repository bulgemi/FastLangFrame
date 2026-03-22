import json
import asyncio
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from .api_models import AgentInvokeRequest, AgentBatchRequest

def create_agent_app(graph: Any, title: str = "FastLangFrame API Server") -> FastAPI:
    """
    LangGraph 객체(또는 Runnable)를 받아 /invoke, /stream, /invoke_batch, /invoke_stream_batch
    엔드포인트가 장착된 FastAPI 앱을 생성하여 반환합니다.
    """
    app = FastAPI(title=title)

    @app.post("/invoke", summary="Agent 실행")
    async def invoke(req: AgentInvokeRequest):
        """단일 Agent 입력을 받아 전체 처리가 끝난 뒤 결과 반환"""
        try:
            result = await graph.ainvoke(req.input, req.config)
            # BaseMessage 등 직렬화 불가능한 객체 처리 (필요시)
            return {"result": result}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    @app.post("/stream", summary="Agent 스트리밍 실행")
    async def stream(req: AgentInvokeRequest):
        """단일 Agent 실행 중 이벤트를 SSE 스트림으로 반환"""
        async def event_generator():
            try:
                async for event in graph.astream(req.input, req.config):
                    yield f"data: {json.dumps(event)}\n\n"
                yield f"data: {json.dumps({'__end__': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.post("/invoke_batch", summary="Agent 배치 실행")
    async def invoke_batch(req: AgentBatchRequest):
        """다수의 입력을 병렬로 처리 후 모든 결과가 완료되면 리스트 리턴"""
        try:
            results = await graph.abatch(req.inputs, req.config)
            return {"results": results}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    @app.post("/invoke_stream_batch", summary="Agent 스트리밍 배치 실행")
    async def invoke_stream_batch(req: AgentBatchRequest):
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
                yield f"data: {json.dumps(item)}\n\n"

            for t in tasks:
                t.cancel()

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app
