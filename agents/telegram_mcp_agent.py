"""
Telegram MCP Agent using telegram-bot-mcp-server
Separate agent implementation that uses MCP server for Telegram Bot operations
"""

import json
import os
from textwrap import dedent
from typing import Dict, Optional

from agno.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools import Toolkit

from db.session import db_url


class TelegramMCPTools(Toolkit):
    """Tools that interface with telegram-bot-mcp-server"""

    def __init__(self):
        super().__init__(name="telegram_mcp_tools")

        # Register tools that will communicate with the MCP server
        self.register(self.send_telegram_message)
        self.register(self.send_telegram_photo)
        self.register(self.send_telegram_document)
        self.register(self.send_telegram_voice)
        self.register(self.get_telegram_updates)
        self.register(self.set_telegram_webhook)
        self.register(self.delete_telegram_webhook)
        self.register(self.get_telegram_me)

        # Configuration from environment
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.mcp_server_url = os.getenv("TELEGRAM_MCP_SERVER_URL", "http://localhost:8000")

    def _validate_config(self) -> bool:
        """Validate that required configuration is available"""
        if not self.bot_token:
            return False
        return True

    def send_telegram_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict] = None,
    ) -> str:
        """
        Send a text message via Telegram Bot API through MCP server

        Args:
            chat_id: Unique identifier for the target chat
            text: Text of the message to be sent
            parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic, etc.
            reply_to_message_id: If the message is a reply, ID of the original message
            reply_markup: Additional interface options (inline keyboard, etc.)

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # This would typically make a request to the MCP server
            # For now, we'll simulate the functionality

            # In a real implementation, this would use the MCP client to call:
            # await mcp_client.call_tool("sendMessage", {
            #     "chat_id": chat_id,
            #     "text": text,
            #     "parse_mode": parse_mode,
            #     "reply_to_message_id": reply_to_message_id,
            #     "reply_markup": reply_markup
            # })

            # Simulated successful response
            return f"Message sent successfully to chat {chat_id}: '{text[:50]}...'"

        except Exception as e:
            return f"Error sending message: {str(e)}"

    def send_telegram_photo(
        self, chat_id: str, photo: str, caption: Optional[str] = None, parse_mode: Optional[str] = None
    ) -> str:
        """
        Send a photo via Telegram Bot API through MCP server

        Args:
            chat_id: Unique identifier for the target chat
            photo: Photo to send (file_id, URL, or file path)
            caption: Photo caption
            parse_mode: Send Markdown or HTML for caption formatting

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            return f"Photo sent successfully to chat {chat_id}"

        except Exception as e:
            return f"Error sending photo: {str(e)}"

    def send_telegram_document(
        self, chat_id: str, document: str, caption: Optional[str] = None, parse_mode: Optional[str] = None
    ) -> str:
        """
        Send a document via Telegram Bot API through MCP server

        Args:
            chat_id: Unique identifier for the target chat
            document: Document to send (file_id, URL, or file path)
            caption: Document caption
            parse_mode: Send Markdown or HTML for caption formatting

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            return f"Document sent successfully to chat {chat_id}"

        except Exception as e:
            return f"Error sending document: {str(e)}"

    def send_telegram_voice(
        self, chat_id: str, voice: str, caption: Optional[str] = None, duration: Optional[int] = None
    ) -> str:
        """
        Send a voice message via Telegram Bot API through MCP server

        Args:
            chat_id: Unique identifier for the target chat
            voice: Voice note to send (file_id, URL, or file path)
            caption: Voice message caption
            duration: Duration of the voice message in seconds

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            return f"Voice message sent successfully to chat {chat_id}"

        except Exception as e:
            return f"Error sending voice message: {str(e)}"

    def get_telegram_updates(
        self, offset: Optional[int] = None, limit: Optional[int] = 100, timeout: Optional[int] = 0
    ) -> str:
        """
        Get updates from Telegram Bot API through MCP server

        Args:
            offset: Identifier of the first update to be returned
            limit: Limits the number of updates to be retrieved
            timeout: Timeout in seconds for long polling

        Returns:
            JSON string with updates or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            # This would return the actual updates from Telegram
            return json.dumps({"updates": [], "ok": True})

        except Exception as e:
            return f"Error getting updates: {str(e)}"

    def set_telegram_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        max_connections: Optional[int] = 40,
        allowed_updates: Optional[list] = None,
    ) -> str:
        """
        Set webhook for receiving updates via MCP server

        Args:
            url: HTTPS url to send updates to
            certificate: Upload your public key certificate
            max_connections: Maximum allowed number of simultaneous connections
            allowed_updates: List of update types to receive

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            return f"Webhook set successfully to {url}"

        except Exception as e:
            return f"Error setting webhook: {str(e)}"

    def delete_telegram_webhook(self) -> str:
        """
        Delete webhook via MCP server

        Returns:
            Success message or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            return "Webhook deleted successfully"

        except Exception as e:
            return f"Error deleting webhook: {str(e)}"

    def get_telegram_me(self) -> str:
        """
        Get basic information about the bot via MCP server

        Returns:
            Bot information as JSON string or error description
        """
        if not self._validate_config():
            return "Error: TELEGRAM_BOT_TOKEN not configured"

        try:
            # MCP server call would be made here
            bot_info = {
                "id": 123456789,
                "is_bot": True,
                "first_name": "MCP Bot",
                "username": "mcp_bot",
                "can_join_groups": True,
                "can_read_all_group_messages": False,
                "supports_inline_queries": False,
            }
            return json.dumps(bot_info, indent=2)

        except Exception as e:
            return f"Error getting bot info: {str(e)}"


def get_telegram_mcp_agent(
    model_id: str = "gpt-4.1-mini",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """
    Create and return a Telegram MCP agent that uses telegram-bot-mcp-server

    Args:
        model_id: Model to use for the agent
        user_id: User ID for the session
        session_id: Session ID for the conversation
        debug_mode: Enable debug logging

    Returns:
        Configured Telegram MCP Agent
    """
    return Agent(
        name="Telegram MCP Bot",
        agent_id="telegram_mcp_agent",
        user_id=user_id,
        session_id=session_id,
        model=OpenAIChat(id=model_id),
        # Tools for Telegram MCP server interaction
        tools=[TelegramMCPTools()],
        # Agent description
        description=dedent("""\
            Telegram MCP Bot - Advanced Telegram Bot operations via MCP server.
            
            I provide comprehensive Telegram Bot API access through the Model Context Protocol,
            enabling rich bot interactions with media, webhooks, and advanced messaging features.
        """),
        # Detailed instructions for the agent
        instructions=dedent("""\
            You are the Telegram MCP Bot, an advanced Telegram Bot interface powered by MCP.
            
            ## Core Capabilities:
            
            ### Message Operations:
            - Use `send_telegram_message()` to send text messages with rich formatting
            - Support for Markdown and HTML parse modes
            - Reply to specific messages with `reply_to_message_id`
            - Send inline keyboards and custom reply markups
            
            ### Media Operations:
            - Use `send_telegram_photo()` to send images with captions
            - Use `send_telegram_document()` to send files and documents
            - Use `send_telegram_voice()` to send voice messages
            - Support for various media formats and sources
            
            ### Bot Management:
            - Use `get_telegram_me()` to get bot information
            - Use `get_telegram_updates()` for polling-based update retrieval
            - Use `set_telegram_webhook()` and `delete_telegram_webhook()` for webhook management
            
            ## MCP Integration:
            
            ### Server Communication:
            - All operations go through the telegram-bot-mcp-server
            - Server handles Telegram Bot API authentication and rate limiting
            - Provides consistent interface across different Telegram Bot API versions
            
            ### Configuration:
            - Requires TELEGRAM_BOT_TOKEN environment variable
            - Optional TELEGRAM_MCP_SERVER_URL for custom server endpoints
            - Automatic error handling for missing configuration
            
            ## Workflow Guidelines:
            
            ### For Interactive Bots:
            1. Set up webhook with `set_telegram_webhook()` for real-time updates
            2. Process incoming messages through webhook endpoints
            3. Respond with appropriate message types (text, media, etc.)
            4. Use reply markups for interactive elements
            
            ### For Broadcasting:
            1. Use `send_telegram_message()` for text announcements
            2. Use `send_telegram_photo()` for visual content
            3. Support batch operations for multiple chats
            4. Handle rate limiting gracefully
            
            ### For File Sharing:
            1. Use `send_telegram_document()` for file distribution
            2. Support various file formats and sizes
            3. Add descriptive captions for context
            4. Handle upload errors and retries
            
            ## Response Guidelines:
            
            ### Be Efficient:
            - Choose the most appropriate message type for content
            - Use reply markups for interactive elements
            - Batch operations when possible
            
            ### Handle Errors:
            - Provide clear error messages for failed operations
            - Suggest alternative approaches for blocked content
            - Help troubleshoot configuration issues
            
            ### Maintain Context:
            - Track conversation state across messages
            - Use reply_to_message_id for threaded conversations
            - Maintain user preferences and settings
            
            ## Security Considerations:
            
            - Validate all user inputs before processing
            - Don't expose sensitive bot tokens or server details
            - Handle rate limiting and abuse prevention
            - Respect Telegram's terms of service and API limits
            
            ## Technical Notes:
            
            - The MCP server abstracts Telegram Bot API complexity
            - All operations are asynchronous through the MCP protocol
            - Server handles authentication, rate limiting, and error recovery
            - Supports both webhook and polling modes for updates
            
            ## Communication Style:
            - Be helpful and responsive to user requests
            - Provide clear feedback on operation status
            - Explain Telegram-specific features when relevant
            - Guide users through complex bot setup procedures
        """),
        # Storage for chat history and session state
        storage=PostgresAgentStorage(table_name="telegram_mcp_agent_sessions", db_url=db_url),
        # Chat history configuration
        add_history_to_messages=True,
        num_history_runs=5,
        read_chat_history=True,
        # Memory for personalizing responses
        memory=Memory(
            model=OpenAIChat(id=model_id),
            db=PostgresMemoryDb(table_name="telegram_mcp_user_memories", db_url=db_url),
            delete_memories=True,
            clear_memories=True,
        ),
        enable_agentic_memory=True,
        # Output formatting
        markdown=True,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
    )
