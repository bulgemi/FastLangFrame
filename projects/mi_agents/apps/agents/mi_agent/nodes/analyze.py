# TODO: 기존 소스에서 usage구하는것 적용했는데 일부만 구한다
import json
from typing import Any

from apps.agents.mi_agent.prompts import language_translation
from apps.agents.mi_agent.prompts.analysis_search_result import build_analysis_prompt
from apps.agents.mi_agent.prompts.language_translation import build_query_langguage_out_prompt
from apps.agents.mi_agent.state.state import MariAgentState
from apps.common.configs.settings import BaseSettings, get_settings
from apps.common.values.enums import ModelPreference
from apps.connectors.llm.llm_client import invoke_llm_function_call


async def generate_analysis(state: MariAgentState) -> MariAgentState:
    #TODO: 유사패턴인 경우 추가
    if {"rdb", "web"}.isdisjoint(get_settings().search_sources):
        state.analysis_content = await _translate_language("관련 문서 검색 내용만 전달 드립니다.(rdb, web검색 요청 없음)")
        return state

    analysis_prompt: str = build_analysis_prompt(metric_data=state.search_output.rdb_search_output.metric_data if state.search_output.rdb_search_output.metric_data else "",
                          web_results="",
                          user_query_language=state.user_query_language,
                          rewrite=state.rewritten_query)
    analysis_text: str = ""
    analysis_text, state.usage  = await _analysis(analysis_prompt)
    language_translation_prompt: str = build_query_langguage_out_prompt(target_lang=state.user_query_language
                                                                        , answer=analysis_text)
    state.analysis_content = await _translate_language(language_translation_prompt)
    return state

async def _analysis(prompt: str)-> tuple[str, dict[str, Any]]:

    response = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        preference=ModelPreference.QUALITY,
        temperature=0.0,
    )

    usage: dict[str, Any] =  response.get("usage", {}) if isinstance(response, dict) else {}
    return response["content"], usage

async def _translate_language(prompt: str)-> str:
    response = invoke_llm_function_call(
        messages=[{"role": "user", "content": prompt}],
        preference=ModelPreference.QUALITY,
    )
    translated_language_analysis: str =response["content"]
    return translated_language_analysis
