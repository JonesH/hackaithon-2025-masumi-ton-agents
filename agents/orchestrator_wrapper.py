"""
Orchestrator Agent Wrapper for Playground Compatibility
Wraps AgentOrchestrator (Team) to make it compatible with Agno Playground interface
"""

from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agents.orchestrator import AgentOrchestrator


class OrchestratorAgentWrapper(Agent):
    """
    Wrapper class that makes AgentOrchestrator compatible with Agno Playground.

    The playground expects Agent objects with initialize_agent() method,
    but AgentOrchestrator inherits from Team which has initialize_team().
    This wrapper bridges the gap.
    """

    def __init__(
        self,
        model_id: str = "gpt-4.1-mini",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        debug_mode: bool = True,
    ):
        # Create the underlying orchestrator
        self._orchestrator = AgentOrchestrator(model_id=model_id)

        # Initialize as an Agent with orchestrator-like properties
        super().__init__(
            name="Agent Orchestrator",
            agent_id="orchestrator_wrapper",
            user_id=user_id,
            session_id=session_id,
            model=OpenAIChat(id=model_id),
            tools=[],  # Tools are handled by the underlying orchestrator
            description="Agent Orchestrator for coordinating multiple specialized agents",
            instructions="""
            You are the Agent Orchestrator, a meta-agent that coordinates multiple specialized AI agents.

            ## Your Role:
            - Route tasks to the most appropriate agent
            - Coordinate multi-agent workflows
            - Combine results from different agents
            - Provide unified responses to users

            ## Available Agents:
            - **Telegram Agent**: Message handling, chat operations
            - **Masumi Agent**: Decentralized agent network navigation
            - **Web Agent**: Internet search and information retrieval
            - **Finance Agent**: Financial data and market information
            - **Telegram MCP Agent**: Advanced Telegram Bot operations

            ## Coordination Patterns:
            - Sequential: One agent after another
            - Parallel: Multiple agents simultaneously
            - Conditional: Based on results or conditions
            - Interactive: Real-time user involvement

            When users ask for tasks that require multiple agents or specialized capabilities,
            I coordinate the appropriate agents to provide comprehensive solutions.
            """,
            markdown=True,
            debug_mode=debug_mode,
        )

    def initialize_agent(self) -> None:
        """
        Initialize the agent (required by playground).
        Delegates to the underlying orchestrator's team initialization.
        """
        try:
            # Initialize the underlying team
            if hasattr(self._orchestrator, 'initialize_team'):
                self._orchestrator.initialize_team()
            elif hasattr(self._orchestrator, 'initialize'):
                self._orchestrator.initialize()
        except Exception as e:
            # If team initialization fails, just log and continue
            if self.debug_mode:
                print(f"Orchestrator team initialization warning: {e}")

    async def arun(self, message: str, stream: bool = False) -> Any:
        """
        Run the orchestrator asynchronously.
        Delegates to the underlying orchestrator's run method.
        """
        try:
            # Try to use the orchestrator's run method
            if hasattr(self._orchestrator, 'arun'):
                return await self._orchestrator.arun(message, stream=stream)
            elif hasattr(self._orchestrator, 'run'):
                return self._orchestrator.run(message, stream=stream)
            else:
                # Fallback to parent agent run
                return await super().arun(message, stream=stream)
        except Exception as e:
            # If orchestrator fails, provide a meaningful response
            error_msg = f"Orchestrator error: {str(e)}"
            if self.debug_mode:
                print(error_msg)

            # Create a simple response object
            class SimpleResponse:
                def __init__(self, content: str):
                    self.content = content

            return SimpleResponse(f"I'm having trouble coordinating the agents right now. Error: {str(e)}")

    def run(self, message: str, stream: bool = False) -> Any:
        """
        Run the orchestrator synchronously.
        Delegates to the underlying orchestrator's run method.
        """
        try:
            if hasattr(self._orchestrator, 'run'):
                return self._orchestrator.run(message, stream=stream)
            else:
                return super().run(message, stream=stream)
        except Exception as e:
            error_msg = f"Orchestrator error: {str(e)}"
            if self.debug_mode:
                print(error_msg)

            class SimpleResponse:
                def __init__(self, content: str):
                    self.content = content

            return SimpleResponse(f"I'm having trouble coordinating the agents right now. Error: {str(e)}")

    def handle_telegram_interaction(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Telegram interactions through the orchestrator.
        """
        return self._orchestrator.handle_telegram_interaction(update)

    def coordinate_masumi_search(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate Masumi Network agent search.
        """
        return self._orchestrator.coordinate_masumi_search(query, user_context)

    def coordinate_financial_analysis(self, query: str, include_web_research: bool = True) -> Dict[str, Any]:
        """
        Coordinate financial analysis with optional web research.
        """
        return self._orchestrator.coordinate_financial_analysis(query, include_web_research)

    def create_workflow(self, workflow_name: str, steps: List[Any], mode: Any = None) -> str:
        """
        Create a new orchestrated workflow.
        """
        return self._orchestrator.create_workflow(workflow_name, steps, mode)

    def execute_workflow(self, workflow_id: str) -> Any:
        """
        Execute a created workflow.
        """
        return self._orchestrator.execute_workflow(workflow_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[Any]:
        """
        Get status of a workflow.
        """
        return self._orchestrator.get_workflow_status(workflow_id)

    def list_active_workflows(self) -> List[Any]:
        """
        List all active workflows.
        """
        return self._orchestrator.list_active_workflows()


def get_orchestrator_wrapper(
    model_id: str = "gpt-4.1-mini",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> OrchestratorAgentWrapper:
    """
    Create and return an orchestrator wrapper instance.

    Args:
        model_id: Model to use for orchestration
        user_id: User ID for the session
        session_id: Session ID for the conversation
        debug_mode: Enable debug logging

    Returns:
        Configured OrchestratorAgentWrapper instance
    """
    return OrchestratorAgentWrapper(
        model_id=model_id,
        user_id=user_id,
        session_id=session_id,
        debug_mode=debug_mode,
    )
