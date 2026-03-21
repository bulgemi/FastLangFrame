import logging
from typing import Optional
from src.common.configs.settings import FastLangFrameSettings, get_settings
from src.common.logging.decorators import log_connector

logger = logging.getLogger(__name__)

class MCPClientManager:
    """Manages connections to standard MCP servers"""
    def __init__(self, settings: Optional[FastLangFrameSettings] = None):
        self.settings = settings or get_settings()
        self.servers = {}
        if self.settings.mcp_server_url:
            self.servers[self.settings.mcp_server_name] = {
                "url": self.settings.mcp_server_url,
                "api_key": self.settings.mcp_server_api_key
            }

    @log_connector
    async def get_server_connection(self, name: str):
        if name not in self.servers:
            raise ValueError(f"MCP server {name} not configured")
        logger.info(f"Connecting to MCP server: {name}")
        return self.servers[name]
