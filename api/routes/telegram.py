from agno.utils.log import logger
from fastapi import APIRouter, Request

from agents.selector import AgentType, get_agent

telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])


@telegram_router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.

    This endpoint receives updates from Telegram and processes them using the SimpleTelegramAgent.
    """
    try:
        # Get the update data from the request
        update_data = await request.json()

        logger.info(f"Received Telegram update: {update_data}")

        # Get the Simple Telegram agent
        agent = get_agent(agent_id=AgentType.SIMPLE_TELEGRAM_AGENT, debug_mode=True)

        # Handle the update using SimpleTelegramAgent's built-in methods
        response = handle_simple_telegram_update(update_data, agent)

        logger.info(f"Agent response: {response}")

        # Return OK status to Telegram (webhook should return 200)
        return {"status": "ok", "processed": True}

    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        raise


@telegram_router.get("/status")
async def telegram_status():
    """
    Check if the Simple Telegram agent is available and configured.
    """
    try:
        agent = get_agent(agent_id=AgentType.SIMPLE_TELEGRAM_AGENT)
        return {"status": "available", "agent_name": agent.name, "agent_id": agent.agent_id}
    except Exception as e:
        logger.error(f"Error checking Simple Telegram agent status: {e}")
        raise


def handle_simple_telegram_update(update_data: dict, agent) -> str:
    """
    Handle incoming Telegram webhook updates using SimpleTelegramAgent.

    Args:
        update_data: The update data from Telegram webhook
        agent: The SimpleTelegramAgent instance

    Returns:
        Response from the agent
    """
    # Use SimpleTelegramAgent's built-in webhook handling
    receive_result = agent.handle_incoming_message(update_data)
    
    if "message" in update_data:
        message = update_data["message"]
        text = message.get("text", "")
        
        # Generate a conversational response using the agent
        response = agent.run(f"User sent message: '{text}'")
        
        # Send the reply back through telegram
        reply_result = agent.send_reply(response.content if response else "I received your message!")
        
        return f"Processed message and sent reply: {reply_result.get('response', 'No response')}"
    
    return f"Received update: {receive_result.get('action', 'unknown')}"
