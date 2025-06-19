from enum import Enum
from typing import List, Optional

from agents.agno_assist import get_agno_assist
from agents.finance_agent import get_finance_agent
from agents.masumi_agent import get_masumi_agent
from agents.orchestrator import get_agent_orchestrator
from agents.simple_telegram_agent import get_simple_telegram_agent
from agents.telegram_agent import get_telegram_agent
from agents.telegram_mcp_agent import get_telegram_mcp_agent
from agents.web_agent import get_web_agent


class AgentType(Enum):
    WEB_AGENT = "web_agent"
    AGNO_ASSIST = "agno_assist"
    FINANCE_AGENT = "finance_agent"
    TELEGRAM_AGENT = "telegram_agent"
    SIMPLE_TELEGRAM_AGENT = "simple_telegram_agent"
    MASUMI_AGENT = "masumi_agent"
    TELEGRAM_MCP_AGENT = "telegram_mcp_agent"
    ORCHESTRATOR = "orchestrator"


def get_available_agents() -> List[str]:
    """Returns a list of all available agent IDs."""
    return [agent.value for agent in AgentType]


def get_agent(
    model_id: str = "gpt-4.1",
    agent_id: Optional[AgentType] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
):
    if agent_id == AgentType.WEB_AGENT:
        return get_web_agent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.AGNO_ASSIST:
        return get_agno_assist(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.FINANCE_AGENT:
        return get_finance_agent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.TELEGRAM_AGENT:
        return get_telegram_agent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.SIMPLE_TELEGRAM_AGENT:
        return get_simple_telegram_agent(
            model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode
        )
    elif agent_id == AgentType.MASUMI_AGENT:
        return get_masumi_agent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.TELEGRAM_MCP_AGENT:
        return get_telegram_mcp_agent(model_id=model_id, user_id=user_id, session_id=session_id, debug_mode=debug_mode)
    elif agent_id == AgentType.ORCHESTRATOR:
        return get_agent_orchestrator(model_id=model_id)

    raise ValueError(f"Agent: {agent_id} not found")
