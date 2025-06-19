"""
Orchestration API Routes
Provides endpoints for agent orchestration and workflow management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agents.orchestrator import OrchestrationMode, WorkflowStep, get_agent_orchestrator
from agents.selector import AgentType


# Pydantic models for API requests/responses
class TelegramUpdateRequest(BaseModel):
    """Request model for Telegram updates"""

    update: Dict[str, Any]


class TelegramMessageRequest(BaseModel):
    """Request model for sending Telegram messages"""

    chat_id: str
    message: str
    reply_markup: Optional[Dict[str, Any]] = None


class MasumiSearchRequest(BaseModel):
    """Request model for Masumi Network searches"""

    query: str
    user_context: Optional[Dict[str, Any]] = None


class FinancialAnalysisRequest(BaseModel):
    """Request model for financial analysis"""

    query: str
    include_web_research: bool = True


class WorkflowStepModel(BaseModel):
    """Pydantic model for workflow steps"""

    agent_type: str
    task_description: str
    depends_on: Optional[List[str]] = None
    condition: Optional[str] = None
    timeout_seconds: Optional[int] = None


class CreateWorkflowRequest(BaseModel):
    """Request model for creating workflows"""

    workflow_name: str
    steps: List[WorkflowStepModel]
    mode: str = "sequential"  # sequential, parallel, conditional, interactive


class WorkflowResponse(BaseModel):
    """Response model for workflow operations"""

    workflow_id: str
    status: str
    steps_completed: List[str]
    steps_failed: List[str]
    results: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


# Initialize router
router = APIRouter(prefix="/orchestration", tags=["orchestration"])

# Global orchestrator instance
orchestrator = get_agent_orchestrator()


@router.post("/telegram/update")
async def handle_telegram_update(request: TelegramUpdateRequest) -> Dict[str, Any]:
    """
    Handle incoming Telegram updates through the orchestrator

    Args:
        request: Telegram update data

    Returns:
        Processing result with routing information
    """
    try:
        result = orchestrator.handle_telegram_interaction(request.update)
        return {"success": True, "result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/telegram/send")
async def send_telegram_message(request: TelegramMessageRequest) -> Dict[str, Any]:
    """
    Send admin message through Telegram orchestrator

    Args:
        request: Message details

    Returns:
        Send result
    """
    try:
        result = orchestrator.telegram_orchestrator.send_admin_message(
            chat_id=request.chat_id, message=request.message, reply_markup=request.reply_markup
        )
        return {"success": True, "result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/masumi/search")
async def coordinate_masumi_search(request: MasumiSearchRequest) -> Dict[str, Any]:
    """
    Coordinate a Masumi Network agent search

    Args:
        request: Search parameters

    Returns:
        Search and coordination results
    """
    try:
        user_context = request.user_context or {}
        result = orchestrator.coordinate_masumi_search(request.query, user_context)
        return {"success": result.get("success", False), "result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finance/analyze")
async def coordinate_financial_analysis(request: FinancialAnalysisRequest) -> Dict[str, Any]:
    """
    Coordinate financial analysis with optional web research

    Args:
        request: Analysis parameters

    Returns:
        Analysis results
    """
    try:
        result = orchestrator.coordinate_financial_analysis(
            query=request.query, include_web_research=request.include_web_research
        )
        return {"success": result.get("success", False), "result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/create")
async def create_workflow(request: CreateWorkflowRequest) -> Dict[str, str]:
    """
    Create a new orchestrated workflow

    Args:
        request: Workflow definition

    Returns:
        Workflow ID and creation status
    """
    try:
        # Convert Pydantic models to WorkflowStep objects
        steps = []
        for step_model in request.steps:
            step = WorkflowStep(
                agent_type=step_model.agent_type,
                task_description=step_model.task_description,
                depends_on=step_model.depends_on,
                condition=step_model.condition,
                timeout_seconds=step_model.timeout_seconds,
            )
            steps.append(step)

        # Parse orchestration mode
        try:
            mode = OrchestrationMode(request.mode)
        except ValueError:
            mode = OrchestrationMode.SEQUENTIAL

        workflow_id = orchestrator.create_workflow(workflow_name=request.workflow_name, steps=steps, mode=mode)

        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": f"Workflow '{request.workflow_name}' created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Execute a created workflow

    Args:
        workflow_id: ID of the workflow to execute
        background_tasks: FastAPI background tasks

    Returns:
        Execution status
    """
    try:
        # Start workflow execution in background
        background_tasks.add_task(orchestrator.execute_workflow, workflow_id)

        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow execution started",
            "status": "running",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str) -> WorkflowResponse:
    """
    Get status of a workflow

    Args:
        workflow_id: ID of the workflow

    Returns:
        Workflow status and results
    """
    try:
        result = orchestrator.get_workflow_status(workflow_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        return WorkflowResponse(
            workflow_id=result.workflow_id,
            status=result.status,
            steps_completed=result.steps_completed,
            steps_failed=result.steps_failed,
            results=result.results,
            start_time=result.start_time,
            end_time=result.end_time,
            error_message=result.error_message,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def list_workflows() -> Dict[str, Any]:
    """
    List all active workflows

    Returns:
        List of workflow statuses
    """
    try:
        workflows = orchestrator.list_active_workflows()

        workflow_summaries = []
        for workflow in workflows:
            workflow_summaries.append(
                {
                    "workflow_id": workflow.workflow_id,
                    "status": workflow.status,
                    "start_time": workflow.start_time.isoformat(),
                    "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                    "steps_completed": len(workflow.steps_completed),
                    "steps_failed": len(workflow.steps_failed),
                }
            )

        return {"success": True, "workflows": workflow_summaries, "total_count": len(workflow_summaries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_available_agents() -> Dict[str, Any]:
    """
    List all available agent types for orchestration

    Returns:
        List of available agents
    """
    try:
        agents = []
        for agent_type in AgentType:
            agents.append(
                {"id": agent_type.value, "name": agent_type.name, "description": _get_agent_description(agent_type)}
            )

        return {"success": True, "agents": agents, "total_count": len(agents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_agent_description(agent_type: AgentType) -> str:
    """Get description for an agent type"""
    descriptions = {
        AgentType.WEB_AGENT: "Web search and information retrieval",
        AgentType.AGNO_ASSIST: "Agno platform assistance and support",
        AgentType.FINANCE_AGENT: "Financial data and market analysis",
        AgentType.TELEGRAM_AGENT: "Basic Telegram bot operations",
        AgentType.SIMPLE_TELEGRAM_AGENT: "Simple Telegram with chat constraints",
        AgentType.MASUMI_AGENT: "Masumi Network navigation and agent hiring",
        AgentType.TELEGRAM_MCP_AGENT: "Advanced Telegram operations via MCP",
        AgentType.ORCHESTRATOR: "Multi-agent coordination and workflows",
    }
    return descriptions.get(agent_type, "Unknown agent type")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for orchestration service

    Returns:
        Service health status
    """
    return {"status": "healthy", "service": "orchestration", "timestamp": datetime.now().isoformat()}
