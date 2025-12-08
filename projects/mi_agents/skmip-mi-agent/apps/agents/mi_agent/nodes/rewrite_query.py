# TODO: 전미숙M작업 내용으로 대체 예정
import json
from typing import Any

from apps.agents.mi_agent.prompts.rdb_search_rewrite_query import (
    build_query_rewrite_prompt,
)
from apps.agents.mi_agent.state.state import MariAgentState
from apps.common.values.enums import ModelPreference
from apps.connectors.llm.llm_client import invoke_llm_function_call


def _convert_histories_to_messages(histories: list) -> list:
    messages = []
    for pair in histories[-5:]:
        user_msg = pair.get("user")
        if user_msg:
            messages.append({"role": "user", "content": user_msg})

        ai_msgs = pair.get("ai", [])
        for ai_msg in ai_msgs:
            text = ai_msg.get("text")
            if text:
                messages.append({"role": "assistant", "content": text})
    return messages


def rewrite_query_node(state: MariAgentState) -> MariAgentState:
    _convert_histories_to_messages(state.histories)

    prompt = build_query_rewrite_prompt(
        parsed_history=state.histories,
        question=state.message,
    )
    response = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        preference=ModelPreference.QUALITY,
        temperature=0.0,
    )

    content: dict[str, Any] = json.loads(response.get("content"))
    state.rewritten_query = content["rewritten_question"]
    state.user_query_language = content["language"]
    return state
