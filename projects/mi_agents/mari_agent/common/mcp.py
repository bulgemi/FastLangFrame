import json
import logging

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from mari_agent.common.config import MCP_CONNECTIONS, mari_config
from mari_agent.common.types.schemas import PromptResource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_mcp_client() -> MultiServerMCPClient:
    """
    MCP 클라이언트를 생성합니다.
    """
    try:
        client = MultiServerMCPClient(connections=MCP_CONNECTIONS)
        logger.info("MCP client created successfully")
        return client
    except Exception as e:
        logger.error(f"Error creating MCP client: {e}")
        raise


async def cleanup_mcp_client(client: MultiServerMCPClient):
    """
    MCP 클라이언트 리소스를 정리합니다.
    """
    if client is not None:
        try:
            # MCP 클라이언트가 close 메서드를 가지고 있다면 호출
            if hasattr(client, "close"):
                await client.close()
            elif hasattr(client, "disconnect"):
                await client.disconnect()
            logger.debug("MCP client resources cleaned up")
        except Exception as cleanup_error:
            logger.warning(f"Error during MCP client cleanup: {cleanup_error}")


async def get_ax_mcp_prompt_resources(prompt_group: str) -> list[PromptResource]:
    """
    MCP 서버에서 프롬프트 리소스 목록을 조회합니다.
    """
    uri = mari_config.AX_MCP_PROMPT_LIST_URL + prompt_group

    mcp_client = await create_mcp_client()
    try:
        resources = await mcp_client.get_resources(
            mari_config.AX_MCP_SERVER_NAME, uris=uri
        )
        if not resources:
            raise ValueError(f"No prompt resources found for tag group: {uri}")

        prompt_resources: list[PromptResource] = []
        for resource in resources:
            prompts = json.loads(resource.data).get("content", [])
            for prompt in prompts:
                prompt_resources.append(PromptResource(**prompt))
        return prompt_resources
    finally:
        await cleanup_mcp_client(mcp_client)


async def get_ax_mcp_prompt_messages(prompt_tags: list[str]) -> list[BaseMessage]:
    """
    MCP 서버에서 prompt_id에 해당하는 프롬프트 메시지 리스트를 반환합니다.
    """
    tags = f"{mari_config.AX_MCP_PROMPT_MARI_TAG_GROUP},{','.join(prompt_tags)}"
    uri = mari_config.AX_MCP_PROMPT_MESSAGE_BY_TAG.format(tags=tags)

    mcp_client = await create_mcp_client()
    try:
        resources = await mcp_client.get_resources(
            mari_config.AX_MCP_SERVER_NAME, uris=[uri]
        )
        if not resources:
            logger.error(f"No resources found for uri: {uri}")
            return []

        prompt_messages: list[BaseMessage] = []
        for resource in resources:
            messages = json.loads(resource.data).get("content", [])
            if not messages:
                logger.error(f"Empty content for resource: {uri}")
                continue

            for message in messages:
                try:
                    if isinstance(message, dict):
                        if message.get("type") == "system":
                            prompt_messages.append(SystemMessage(**message))
                        elif message.get("type") == "human":
                            prompt_messages.append(HumanMessage(**message))
                    else:
                        logger.error(f"Message is not a dict: {message}")
                except Exception as e:
                    logger.error(f"Failed to create BaseMessage: {e}")

        return prompt_messages
    finally:
        await cleanup_mcp_client(mcp_client)
