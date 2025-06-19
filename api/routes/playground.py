from logging import getLogger

from agno.playground import Playground

from agents.selector import AgentType, get_agent

logger = getLogger(__name__)

######################################################
## Routes for the Playground Interface
######################################################

def get_playground_agents():
    """Get all available agents for the playground interface."""
    agents = []

    # Iterate through all available agent types
    for agent_type in AgentType:
        try:
            agent = get_agent(
                model_id="gpt-4.1-mini",
                agent_id=agent_type,
                debug_mode=True
            )
            agents.append(agent)
            logger.info(f"Successfully loaded agent: {agent_type.value}")
        except Exception as e:
            logger.warning(f"Failed to load agent {agent_type.value}: {e}")
            # Continue loading other agents even if one fails
            continue

    return agents

# Get all available agents for the playground
playground_agents = get_playground_agents()

# Create a playground instance with all available agents
playground = Playground(agents=playground_agents)

# Get the router for the playground
playground_router = playground.get_async_router()
