import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List

from dateutil import parser as date_parser
from tavily import TavilyClient

from research_agent.common.config import get_mari_config
from research_agent.common.types.nodes import (
    DataSearchToolNodeInput,
    DataSearchToolNodeOutput,
)
from research_agent.graph.tools.tool_manager import BaseSearchTool

mari_config = get_mari_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchTool(BaseSearchTool):
    """웹 뉴스/이벤트 검색을 수행하는 도구"""

    @property
    def name(self) -> str:
        return "WebSearchTool"

    @property
    def description(self) -> str:
        return (
            "Search web for news and events related oil prices over specified periods."
        )

    def __init__(self):
        self._client = None

    @property
    def client(self) -> TavilyClient:
        if self._client is None:
            self._client = TavilyClient(mari_config.TAVILY_API_KEY)
        return self._client

    def _split_periods(self, period: Dict[str, str]) -> List[Dict[str, str]]:
        start_date = datetime.strptime(period["start"], "%Y-%m-%d")
        end_date = datetime.strptime(period["end"], "%Y-%m-%d")

        today = datetime.now().date()
        if start_date.date() >= today:
            yesterday = today - timedelta(days=1)
            start_date = datetime.combine(yesterday, datetime.min.time())

        if end_date.date() > today:
            end_date = datetime.combine(today, datetime.min.time())

        total_days = (end_date - start_date).days + 1

        if total_days <= 7:
            chunk_days = 3
        elif total_days <= 15:
            chunk_days = 5
        elif total_days <= 30:
            chunk_days = 7
        elif total_days <= 90:
            chunk_days = 10
        elif total_days <= 180:
            chunk_days = 15
        else:
            chunk_days = 30

        periods = []
        current_date = start_date

        while current_date <= end_date:
            chunk_end = min(current_date + timedelta(days=chunk_days - 1), end_date)
            periods.append(
                {
                    "start": current_date.strftime("%Y-%m-%d"),
                    "end": chunk_end.strftime("%Y-%m-%d"),
                }
            )
            current_date = chunk_end + timedelta(days=1)

        logger.info(
            f"Split period into {len(periods)} chunks with {chunk_days}-day intervals"
        )
        return periods

    async def _search_period(
        self,
        query: str,
        period: Dict[str, str],
        search_params: Dict[str, Any],
        result_filter: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        start_date = period.get("start", "")
        end_date = period.get("end", "")

        if not start_date or start_date == end_date:
            start_date, end_date = self._get_published_date_range(start_date)

        period_search_params = search_params.copy()
        period_search_params["start_date"] = start_date
        period_search_params["end_date"] = end_date

        if not hasattr(self.__class__, "_semaphore"):
            self.__class__._semaphore = asyncio.Semaphore(
                mari_config.TAVILY_MAX_CONCURRENT_REQUESTS
            )

        async with self.__class__._semaphore:
            executor = TavilyExecutor.get_executor()
            loop = asyncio.get_event_loop()
            search_func = functools.partial(
                self.client.search, query, **period_search_params
            )
            response = await loop.run_in_executor(executor, search_func)

        results = self._filter_results_by_score(
            response["results"],
            result_filter.get("score_threshold", mari_config.TAVILY_SCORE_THRESHOLD),
        )

        # 메타데이터 추가 - 인덱싱은 상위에서 처리하므로 제거
        period_str = f"{start_date}_{end_date}"
        for result in results:
            if isinstance(result, dict):
                result["period"] = period_str
                result["search_query"] = query

        logger.info(
            f"🔍 web [{period_str}] {query}: {len(results)} results, {response['response_time']}ms"
        )
        return results

    def _get_published_date_range(
        self, base_date: str, window_days: int = 1
    ) -> tuple[str, str]:
        if not base_date:
            base_date = datetime.now().date()
        else:
            base_date = date_parser.parse(base_date.strip()).date()

        start_date = base_date - timedelta(days=window_days)
        end_date = base_date + timedelta(days=window_days)

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def _filter_results_by_score(
        self, data_list: List[Dict], score_threshold: float
    ) -> List[Dict]:
        """점수 기준으로 결과 필터링"""
        return [data for data in data_list if data.get("score", 0.0) >= score_threshold]

    async def search(self, input: DataSearchToolNodeInput) -> DataSearchToolNodeOutput:
        """웹 검색 실행 로직"""
        try:
            query = input.period_query.query
            periods = self._split_periods(input.period_query.period)

            tavily_config = mari_config.TAVILY_CONFIG_JSON
            search_params = tavily_config.get("search_params", {})
            result_filter = tavily_config.get("result_filter", {})

            tasks = [
                self._search_period(query, period, search_params, result_filter)
                for period in periods
            ]

            period_results = await asyncio.gather(*tasks)

            results = []
            index = 1

            for sublist in period_results:
                if isinstance(sublist, list):
                    for result in sublist:
                        if isinstance(result, dict):
                            result["index"] = f"web_{index}"
                            index += 1
                        results.append(result)
                elif sublist and isinstance(sublist, dict):
                    sublist["index"] = f"web_{index}"
                    index += 1
                    results.append(sublist)

            logger.info(f"Web search completed: {len(results)} results found")
            return DataSearchToolNodeOutput(web_data=results)

        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return DataSearchToolNodeOutput()


class IntervalEventMapperTool(BaseSearchTool):
    @property
    def name(self) -> str:
        return "IntervalEventMapperTool"

    @property
    def description(self) -> str:
        return "Map events to specified time intervals"

    async def search(self, input: DataSearchToolNodeInput) -> DataSearchToolNodeOutput:
        # 이벤트 매핑 로직
        return DataSearchToolNodeOutput()


class TavilyExecutor:
    """Tavily API 호출을 위한 Thread Pool 관리자"""

    _instance = None
    _executor = None

    @classmethod
    def get_executor(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._executor = ThreadPoolExecutor(
                max_workers=mari_config.TAVILY_MAX_CONCURRENT_REQUESTS,
                thread_name_prefix="tavily_search",
            )
        return cls._executor

    @classmethod
    def shutdown(cls):
        if cls._executor:
            cls._executor.shutdown(wait=True)
            cls._executor = None
            cls._instance = None


# 애플리케이션 종료 시 리소스 정리
def cleanup_tavily_resources():
    TavilyExecutor.shutdown()
