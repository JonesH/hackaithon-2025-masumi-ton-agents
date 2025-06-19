from textwrap import dedent
from typing import Optional
import os

from agno.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools import Toolkit

from telegram import Bot

from db.session import db_url


class TelegramTools(Toolkit):
    def __init__(self):
        super().__init__(name="telegram_tools")
        self.register(self.send_message)

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
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

        bot = Bot(token=bot_token)
        
        message = bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_to_message_id=reply_to_message_id
        )
        
        return f"Message sent successfully. Message ID: {message.message_id}"


def get_telegram_agent(
    model_id: str = "gpt-4.1-mini",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    return Agent(
        name="Telegram Assistant",
        agent_id="telegram_assistant",
        user_id=user_id,
        session_id=session_id,
        model=OpenAIChat(id=model_id),
        # Tools available to the agent
        tools=[TelegramTools()],
        # Description of the agent
        description=dedent("""\
            You are a Telegram Assistant, an AI agent designed to interact with users through Telegram.

            You can send messages to Telegram chats and respond to incoming messages intelligently.
        """),
        # Instructions for the agent
        instructions=dedent("""\
            You are a Telegram Assistant with the following capabilities and guidelines:

            ## Core Function:
            - You are an intelligent AI assistant that operates through Telegram
            - You can send messages to Telegram chats using the send_message tool
            - You respond to user queries with helpful, accurate, and concise information

            ## Message Handling:
            - When asked to send a message, use the send_message tool with the appropriate chat_id and text
            - Format your Telegram messages clearly and use Markdown when helpful
            - Keep responses conversational and friendly, suitable for chat environments
            - If replying to a specific message, include the reply_to_message_id parameter

            ## Response Guidelines:
            - Be helpful, informative, and engaging in your responses
            - Adapt your tone to be casual and friendly for Telegram conversations
            - Provide clear, actionable information when possible
            - If you cannot help with something, explain why clearly

            ## Technical Notes:
            - Always verify you have the necessary information (chat_id) before sending messages
            - Handle errors gracefully and inform the user if something goes wrong
            - Your direct responses (not sent via send_message tool) will continue to go to the playground interface

            ## Memory and Context:
            - Remember user preferences and conversation context
            - Use your memory to provide personalized responses over time
            - The user's name might be different from the user_id, you may ask for it if needed and add it to your memory if they share it with you.
        """),
        # -*- Storage -*-
        # Storage chat history and session state in a Postgres table
        storage=PostgresAgentStorage(table_name="telegram_agent_sessions", db_url=db_url),
        # -*- History -*-
        # Send the last 5 messages from the chat history (more context for conversations)
        add_history_to_messages=True,
        num_history_runs=5,
        # Add a tool to read the chat history if needed
        read_chat_history=True,
        # -*- Memory -*-
        # Enable agentic memory where the Agent can personalize responses to the user
        memory=Memory(
            model=OpenAIChat(id=model_id),
            db=PostgresMemoryDb(table_name="telegram_user_memories", db_url=db_url),
            delete_memories=True,
            clear_memories=True,
        ),
        enable_agentic_memory=True,
        # -*- Other settings -*-
        # Format responses using markdown
        markdown=True,
        # Add the current date and time to the instructions
        add_datetime_to_instructions=True,
        # Show debug logs
        debug_mode=debug_mode,
    )


# Webhook handler for incoming Telegram updates
def handle_telegram_update(update_data: dict, agent: Agent) -> str:
    """
    Handle incoming Telegram webhook updates.

    Args:
        update_data: The update data from Telegram webhook
        agent: The telegram agent instance

    Returns:
        Response from the agent
    """
    # Extract message data
    if "message" in update_data:
        message = update_data["message"]
        chat_id = str(message["chat"]["id"])
        user_id = str(message["from"]["id"])
        text = message.get("text", "")

        # Set agent session context
        agent.user_id = user_id
        agent.session_id = f"telegram_{chat_id}"

        # Create context for the agent
        context = f"User sent message in Telegram chat {chat_id}: '{text}'"
        if message.get("reply_to_message"):
            context += f" (replying to message ID {message['reply_to_message']['message_id']})"

        # Get agent response
        response = agent.run(context)

        return response.content if response else "No response generated"
    
    return "No message found in update"
