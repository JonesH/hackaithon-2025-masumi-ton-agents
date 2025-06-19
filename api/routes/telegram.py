from fastapi import APIRouter, Request, HTTPException
from agno.utils.log import logger

from agents.selector import AgentType, get_agent
from agents.telegram_agent import handle_telegram_update

telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])


@telegram_router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates.
    
    This endpoint receives updates from Telegram and processes them using the telegram agent.
    """
    try:
        # Get the update data from the request
        update_data = await request.json()
        
        logger.info(f"Received Telegram update: {update_data}")
        
        # Get the telegram agent
        agent = get_agent(
            agent_id=AgentType.TELEGRAM_AGENT,
            debug_mode=True
        )
        
        # Handle the update
        response = handle_telegram_update(update_data, agent)
        
        logger.info(f"Agent response: {response}")
        
        # Return OK status to Telegram (webhook should return 200)
        return {"status": "ok", "processed": True}
        
    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@telegram_router.get("/status")
async def telegram_status():
    """
    Check if the Telegram agent is available and configured.
    """
    try:
        agent = get_agent(agent_id=AgentType.TELEGRAM_AGENT)
        return {
            "status": "available",
            "agent_name": agent.name,
            "agent_id": agent.agent_id
        }
    except Exception as e:
        logger.error(f"Error checking Telegram agent status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
