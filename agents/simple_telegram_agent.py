"""
Simple Telegram Agent with Chat ID Constraint Logic
Handles basic message sending/receiving with proper chat_id constraints
"""

import os
from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Toolkit
from telegram import Bot


@dataclass
class MessageContext:
    """Message context for chat_id constraint logic"""

    is_reply_to_incoming: bool
    incoming_chat_id: Optional[str] = None
    admin_initiated: bool = False


class SimpleTelegramTools(Toolkit):
    """Simple Telegram tools with constraint-aware message sending"""

    def __init__(self):
        super().__init__(name="simple_telegram_tools")
        self.register(self.send_message)
        self.register(self.admin_send_message)

    def send_message(self, chat_id: str, text: str, reply_to_message_id: Optional[int] = None) -> str:
        """
        Send a message to a Telegram chat.

        Args:
            chat_id: The chat ID to send the message to
            text: The message text to send
            reply_to_message_id: Optional message ID to reply to

        Returns:
            Success/failure message
        """
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return "Error: TELEGRAM_BOT_TOKEN environment variable not set"

        try:
            bot = Bot(token=bot_token)
            message = bot.send_message(
                chat_id=chat_id, text=text, parse_mode="Markdown", reply_to_message_id=reply_to_message_id
            )
            return f"Message sent successfully to chat {chat_id}. Message ID: {message.message_id}"
        except Exception as e:
            return f"Failed to send message: {str(e)}"

    def admin_send_message(self, chat_id: str, text: str, reply_markup: Optional[dict] = None) -> str:
        """
        Admin-initiated message sending (can specify any chat_id)

        Args:
            chat_id: The chat ID to send the message to
            text: The message text to send
            reply_markup: Optional inline keyboard markup

        Returns:
            Success/failure message
        """
        return self.send_message(chat_id, text)


class SimpleTelegramAgent(Agent):
    """Simple Telegram agent with chat_id constraint logic"""

    def __init__(
        self,
        model_id: str = "gpt-4.1-mini",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = True,
    ):
        super().__init__(
            name="Simple Telegram Agent",
            agent_id="simple_telegram_agent",
            user_id=user_id,
            session_id=session_id,
            model=OpenAIChat(id=model_id),
            tools=[SimpleTelegramTools()],
            description="Simple Telegram agent with chat_id constraint logic",
            instructions=dedent("""
                You are a Simple Telegram Agent with context-aware capabilities:
                
                ## Context Awareness:
                - **Playground Mode**: When used via playground interface, respond normally with text
                - **Telegram Mode**: When handling telegram webhooks, use telegram tools appropriately
                - **Explicit Mode**: Only use telegram tools when explicitly asked to send telegram messages
                
                ## Core Functions:
                - Handle incoming Telegram messages (when in telegram mode)
                - Send message replies with chat_id constraints (when explicitly requested or in telegram mode)
                - Send admin messages (when explicitly requested)
                
                ## Interaction Guidelines:
                - **Default behavior**: Respond with normal conversational text
                - **Use telegram tools only when**:
                  1. User explicitly asks to "send a telegram message" or similar
                  2. User provides specific chat_id and asks to send message
                  3. Currently in telegram webhook mode (handling incoming telegram messages)
                
                ## Chat ID Constraint Rules (when using telegram tools):
                - When replying to incoming message: MUST use incoming chat_id (cannot change)
                - When admin initiates send: CAN specify any chat_id
                
                ## Response Guidelines:
                - Be helpful and conversational in all contexts
                - For playground conversations: respond with normal text
                - For telegram operations: format messages clearly and confirm actions
                - Handle errors gracefully and explain what went wrong
                - Always indicate whether you're responding via text or telegram
            """),
            markdown=True,
            debug_mode=debug_mode,
        )

        # Track current message context for chat_id constraints
        self.current_context: Optional[MessageContext] = None
        # Track interaction mode (playground, telegram_webhook, explicit)
        self.interaction_mode: str = "playground"

    def handle_incoming_message(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Telegram message and set reply context

        Args:
            update: Telegram update data

        Returns:
            Processing result with context information
        """
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        user_id = str(message.get("from", {}).get("id", ""))
        text = message.get("text", "")

        # Set context for potential replies and telegram mode
        self.current_context = MessageContext(
            is_reply_to_incoming=True, incoming_chat_id=chat_id, admin_initiated=False
        )
        self.interaction_mode = "telegram_webhook"

        result = {
            "action": "message_received",
            "chat_id": chat_id,
            "user_id": user_id,
            "message_text": text,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "context_set": "reply_mode",
            "reply_chat_id_locked": chat_id,
        }

        return result

    def send_reply(self, text: str, reply_markup: Optional[dict] = None) -> Dict[str, Any]:
        """
        Send reply to current chat (chat_id locked from incoming message)

        Args:
            text: Reply text
            reply_markup: Optional inline keyboard

        Returns:
            Send result with constraint information
        """
        if not self.current_context or not self.current_context.is_reply_to_incoming:
            return {"action": "reply_failed", "error": "No incoming message to reply to", "success": False}

        chat_id = self.current_context.incoming_chat_id

        # Only send via telegram if in telegram mode
        if self.interaction_mode == "telegram_webhook":
            # Use the agent's run method to send the message
            context_msg = f"Send a message to Telegram chat {chat_id}: '{text}'"
            response = self.run(context_msg)
            
            # Clear reply context after sending
            self.current_context = None
            self.interaction_mode = "playground"  # Reset to default

            return {
                "action": "reply_sent",
                "chat_id": chat_id,
                "text": text,
                "mode": "reply_to_incoming",
                "chat_id_locked": True,
                "response": response.content if response else "No response",
                "success": True,
            }
        else:
            # Just return the text without sending telegram message
            return {
                "action": "text_reply",
                "text": text,
                "mode": "text_only",
                "chat_id_locked": False,
                "response": text,
                "success": True,
            }

    def send_admin_message(self, chat_id: str, text: str, reply_markup: Optional[dict] = None) -> Dict[str, Any]:
        """
        Admin-initiated message sending (admin can specify any chat_id)

        Args:
            chat_id: Target chat ID
            text: Message text
            reply_markup: Optional inline keyboard

        Returns:
            Send result
        """
        # Set admin context and explicit mode for telegram sending
        self.current_context = MessageContext(is_reply_to_incoming=False, admin_initiated=True)
        self.interaction_mode = "explicit"

        # Use the agent's run method to send the message
        context_msg = f"Send an admin message to Telegram chat {chat_id}: '{text}'"
        response = self.run(context_msg)

        # Clear context after sending
        self.current_context = None
        self.interaction_mode = "playground"  # Reset to default

        return {
            "action": "admin_sent",
            "chat_id": chat_id,
            "text": text,
            "mode": "admin_initiated",
            "chat_id_locked": False,
            "response": response.content if response else "No response",
            "success": True,
        }

    def set_interaction_mode(self, mode: str) -> None:
        """
        Set the interaction mode for context awareness.
        
        Args:
            mode: One of 'playground', 'telegram_webhook', 'explicit'
        """
        self.interaction_mode = mode


def get_simple_telegram_agent(
    model_id: str = "gpt-4.1-mini",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> SimpleTelegramAgent:
    """
    Create and return a simple telegram agent instance

    Args:
        model_id: Model to use for the agent
        user_id: User ID for the session
        session_id: Session ID for the conversation
        debug_mode: Enable debug logging

    Returns:
        Configured SimpleTelegramAgent instance
    """
    return SimpleTelegramAgent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
