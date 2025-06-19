"""
Agent Orchestrator for Coordinating Multiple Agents
Manages workflows between Telegram, Masumi Network, and other agents
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.models.openai import OpenAIChat
from agno.team import Team

from agents.finance_agent import get_finance_agent
from agents.masumi_agent import get_masumi_agent
from agents.simple_telegram_agent import get_simple_telegram_agent
from agents.telegram_mcp_agent import get_telegram_mcp_agent
from agents.web_agent import get_web_agent


class OrchestrationMode(Enum):
    """Different orchestration modes for agent coordination"""

    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"  # Agents work simultaneously
    CONDITIONAL = "conditional"  # Agents work based on conditions
    INTERACTIVE = "interactive"  # Real-time user interaction


@dataclass
class WorkflowStep:
    """Represents a single step in an orchestrated workflow"""

    agent_type: str
    task_description: str
    depends_on: Optional[List[str]] = None
    condition: Optional[str] = None
    timeout_seconds: Optional[int] = None


@dataclass
class OrchestrationResult:
    """Result of an orchestrated workflow"""

    workflow_id: str
    status: str  # "running", "completed", "failed", "timeout"
    steps_completed: List[str]
    steps_failed: List[str]
    results: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


class TelegramOrchestrator:
    """Orchestrator specifically for Telegram-based workflows"""

    def __init__(self, model_id: str = "gpt-4.1-mini"):
        self.model_id = model_id
        self.telegram_agent = get_simple_telegram_agent(model_id=model_id)
        self.active_workflows: Dict[str, OrchestrationResult] = {}

    def handle_telegram_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming Telegram update with intelligent routing

        Args:
            update: Telegram update data

        Returns:
            Processing result with routing information
        """
        message = update.get("message", {})
        text = message.get("text", "").lower()

        # Process the incoming message
        receive_result = self.telegram_agent.handle_incoming_message(update)

        # Intelligent routing based on message content
        route_decision = self._route_message(text)

        if route_decision["requires_reply"]:
            reply_result = self.telegram_agent.send_reply(
                text=route_decision["reply_text"], reply_markup=route_decision.get("reply_markup")
            )

            return {
                "operation": "telegram_reply",
                "receive_result": receive_result,
                "reply_result": reply_result,
                "route_decision": route_decision,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "operation": "telegram_received",
            "receive_result": receive_result,
            "route_decision": route_decision,
            "timestamp": datetime.now().isoformat(),
        }

    def _route_message(self, text: str) -> Dict[str, Any]:
        """
        Route message to appropriate workflow based on content

        Args:
            text: Message text (lowercased)

        Returns:
            Routing decision with reply information
        """
        # Masumi Network keywords
        masumi_keywords = ["masumi", "hire agent", "find agent", "agent network", "blockchain agent"]

        # Financial keywords
        finance_keywords = ["stock", "price", "financial", "market", "trading", "investment"]

        # Web search keywords
        web_keywords = ["search", "find information", "lookup", "google", "web"]

        # Help keywords
        help_keywords = ["help", "start", "hello", "hi", "what can you do"]

        if any(keyword in text for keyword in masumi_keywords):
            return {
                "requires_reply": True,
                "reply_text": "🌐 I can help you navigate the Masumi Network! I can:\n\n• Find available AI agents\n• Help you hire agents for tasks\n• Monitor job progress\n• Manage payments\n\nWhat would you like to do?",
                "suggested_workflow": "masumi_network",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🔍 Find Agents", "callback_data": "masumi_list"}],
                        [{"text": "💼 Hire Agent", "callback_data": "masumi_hire"}],
                        [{"text": "📊 Check Jobs", "callback_data": "masumi_status"}],
                    ]
                },
            }

        elif any(keyword in text for keyword in finance_keywords):
            return {
                "requires_reply": True,
                "reply_text": "📈 I can help with financial information! I can:\n\n• Get stock prices\n• Market analysis\n• Financial news\n• Investment data\n\nWhat financial information do you need?",
                "suggested_workflow": "finance_agent",
            }

        elif any(keyword in text for keyword in web_keywords):
            return {
                "requires_reply": True,
                "reply_text": "🔍 I can search the web for you! I can:\n\n• Find current information\n• Research topics\n• Get latest news\n• Look up facts\n\nWhat would you like me to search for?",
                "suggested_workflow": "web_agent",
            }

        elif any(keyword in text for keyword in help_keywords):
            return {
                "requires_reply": True,
                "reply_text": "👋 Hello! I'm your AI Agent Orchestrator. I can help you with:\n\n🌐 **Masumi Network** - Find and hire AI agents\n📈 **Finance** - Stock prices and market data\n🔍 **Web Search** - Find information online\n📱 **Telegram** - Advanced bot operations\n\nJust tell me what you need!",
                "suggested_workflow": "help",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🌐 Masumi Network", "callback_data": "help_masumi"}],
                        [{"text": "📈 Finance", "callback_data": "help_finance"}],
                        [{"text": "🔍 Web Search", "callback_data": "help_web"}],
                        [{"text": "📱 Telegram Bot", "callback_data": "help_telegram"}],
                    ]
                },
            }

        else:
            return {
                "requires_reply": True,
                "reply_text": f'I received your message: "{text}"\n\nI can help you with various tasks. Type "help" to see what I can do!',
                "suggested_workflow": "general_response",
            }

    def send_admin_message(self, chat_id: str, message: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send admin message through Telegram agent

        Args:
            chat_id: Target chat ID
            message: Message text
            reply_markup: Optional inline keyboard

        Returns:
            Send result
        """
        result = self.telegram_agent.send_admin_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

        return {"operation": "admin_message", "result": result, "timestamp": datetime.now().isoformat()}


class AgentOrchestrator(Team):
    """Main orchestrator for coordinating multiple specialized agents"""

    def __init__(self, model_id: str = "gpt-4.1-mini"):
        self.model_id = model_id

        # Initialize specialized agents
        self.telegram_agent = get_simple_telegram_agent(model_id=model_id)
        self.masumi_agent = get_masumi_agent(model_id=model_id)
        self.telegram_mcp_agent = get_telegram_mcp_agent(model_id=model_id)
        self.web_agent = get_web_agent(model_id=model_id)
        self.finance_agent = get_finance_agent(model_id=model_id)

        # Initialize the team
        super().__init__(
            name="Agent Orchestrator",
            mode="coordinate",
            model=OpenAIChat(model_id),
            members=[self.telegram_agent, self.masumi_agent, self.web_agent, self.finance_agent],
            instructions=dedent("""
                You are the Agent Orchestrator, coordinating multiple specialized AI agents.
                
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
                
                Always choose the most efficient approach for each task.
            """),
            enable_agentic_context=True,
            show_members_responses=True,
            markdown=True,
        )

        # Workflow management
        self.active_workflows: Dict[str, OrchestrationResult] = {}
        self.telegram_orchestrator = TelegramOrchestrator(model_id=model_id)

    def create_workflow(
        self, workflow_name: str, steps: List[WorkflowStep], mode: OrchestrationMode = OrchestrationMode.SEQUENTIAL
    ) -> str:
        """
        Create a new orchestrated workflow

        Args:
            workflow_name: Name for the workflow
            steps: List of workflow steps
            mode: Orchestration mode

        Returns:
            Workflow ID
        """
        workflow_id = f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = OrchestrationResult(
            workflow_id=workflow_id,
            status="created",
            steps_completed=[],
            steps_failed=[],
            results={},
            start_time=datetime.now(),
        )

        self.active_workflows[workflow_id] = result
        return workflow_id

    def execute_workflow(self, workflow_id: str) -> OrchestrationResult:
        """
        Execute a created workflow

        Args:
            workflow_id: ID of the workflow to execute

        Returns:
            Workflow execution result
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.active_workflows[workflow_id]
        workflow.status = "running"

        # This would contain the actual workflow execution logic
        # For now, we'll simulate a successful completion
        workflow.status = "completed"
        workflow.end_time = datetime.now()

        return workflow

    def handle_telegram_interaction(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Telegram interaction through the telegram orchestrator

        Args:
            update: Telegram update data

        Returns:
            Interaction result
        """
        return self.telegram_orchestrator.handle_telegram_update(update)

    def coordinate_masumi_search(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate a Masumi Network agent search

        Args:
            query: Search query for agents
            user_context: User context and preferences

        Returns:
            Search and coordination results
        """
        try:
            # Step 1: Search for agents
            search_prompt = f"Search for agents related to: {query}"
            masumi_response = self.masumi_agent.run(search_prompt)

            # Step 2: If web research is needed, use web agent
            if "more information needed" in masumi_response.content.lower():
                web_prompt = f"Research information about: {query}"
                web_response = self.web_agent.run(web_prompt)

                # Step 3: Combine results
                combined_prompt = f"Based on Masumi results: {masumi_response.content}\nAnd web research: {web_response.content}\nProvide a comprehensive summary for the user."
                final_response = self.run(combined_prompt)

                return {
                    "workflow": "masumi_with_web_research",
                    "masumi_result": masumi_response.content,
                    "web_result": web_response.content,
                    "combined_result": final_response.content,
                    "success": True,
                }

            return {"workflow": "masumi_only", "masumi_result": masumi_response.content, "success": True}

        except Exception as e:
            return {"workflow": "masumi_search_failed", "error": str(e), "success": False}

    def coordinate_financial_analysis(self, query: str, include_web_research: bool = True) -> Dict[str, Any]:
        """
        Coordinate financial analysis with optional web research

        Args:
            query: Financial query
            include_web_research: Whether to include web research

        Returns:
            Analysis results
        """
        try:
            # Step 1: Get financial data
            finance_response = self.finance_agent.run(query)

            results = {"workflow": "financial_analysis", "finance_result": finance_response.content, "success": True}

            # Step 2: Optional web research for context
            if include_web_research:
                web_query = f"Latest news and analysis about: {query}"
                web_response = self.web_agent.run(web_query)

                # Step 3: Combine financial data with web research
                combined_prompt = f"""
                Combine this financial data: {finance_response.content}
                With this market context: {web_response.content}
                Provide a comprehensive financial analysis.
                """
                final_response = self.run(combined_prompt)

                results.update(
                    {
                        "workflow": "financial_analysis_with_research",
                        "web_result": web_response.content,
                        "combined_result": final_response.content,
                    }
                )

            return results

        except Exception as e:
            return {"workflow": "financial_analysis_failed", "error": str(e), "success": False}

    def get_workflow_status(self, workflow_id: str) -> Optional[OrchestrationResult]:
        """
        Get status of a workflow

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow status or None if not found
        """
        return self.active_workflows.get(workflow_id)

    def list_active_workflows(self) -> List[OrchestrationResult]:
        """
        List all active workflows

        Returns:
            List of active workflow results
        """
        return list(self.active_workflows.values())


def get_agent_orchestrator(model_id: str = "gpt-4.1-mini") -> AgentOrchestrator:
    """
    Create and return an agent orchestrator instance

    Args:
        model_id: Model to use for orchestration

    Returns:
        Configured AgentOrchestrator instance
    """
    return AgentOrchestrator(model_id=model_id)
