from typing import List

from pydantic import BaseModel, ConfigDict, Field

from mcp_agent.workflows.orchestrator.orchestrator_prompts import (
    PLAN_RESULT_TEMPLATE,
    STEP_RESULT_TEMPLATE,
    TASK_RESULT_TEMPLATE,
)


class Task(BaseModel):
    """An individual task that needs to be executed"""

    description: str = Field(description="Description of the task")


class ServerTask(Task):
    """An individual task that can be accomplished by one or more MCP servers"""

    servers: List[str] = Field(
        description="Names of MCP servers that the LLM has access to for this task",
        default_factory=list,
    )


class AgentTask(Task):
    """An individual task that can be accomplished by an Agent."""

    agent: str = Field(
        description="Name of Agent from given list of agents that the LLM has access to for this task",
    )


class Step(BaseModel):
    """A step containing independent tasks that can be executed in parallel"""

    description: str = Field(description="Description of the step")

    tasks: List[AgentTask] = Field(
        description="Subtasks that can be executed in parallel",
        default_factory=list,
    )


class Plan(BaseModel):
    """Plan generated by the orchestrator planner."""

    steps: List[Step] = Field(
        description="List of steps to execute sequentially",
        default_factory=list,
    )
    is_complete: bool = Field(
        description="Whether the overall plan objective is complete"
    )


class TaskWithResult(Task):
    """An individual task with its result"""

    result: str = Field(
        description="Result of executing the task", default="Task completed"
    )
    
    agent: str = Field(
        description="Name of the agent that executed this task",
        default=""
    )

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class StepResult(BaseModel):
    """Result of executing a step"""

    step: Step = Field(description="The step that was executed", default_factory=Step)
    task_results: List[TaskWithResult] = Field(
        description="Results of executing each task", default_factory=list
    )
    result: str = Field(
        description="Result of executing the step", default="Step completed"
    )

    def add_task_result(self, task_result: TaskWithResult):
        """Add a task result to this step"""
        if not isinstance(self.task_results, list):
            self.task_results = []
        self.task_results.append(task_result)


class PlanResult(BaseModel):
    """Results of executing a plan"""

    objective: str
    """Objective of the plan"""

    plan: Plan | None = None
    """The plan that was executed"""

    step_results: List[StepResult]
    """Results of executing each step"""

    is_complete: bool = False
    """Whether the overall plan objective is complete"""

    result: str | None = None
    """Result of executing the plan"""

    def add_step_result(self, step_result: StepResult):
        """Add a step result to this plan"""
        if not isinstance(self.step_results, list):
            self.step_results = []
        self.step_results.append(step_result)


class NextStep(Step):
    """Single next step in iterative planning"""

    is_complete: bool = Field(
        description="Whether the overall plan objective is complete"
    )


def format_task_result_text(task_result: TaskWithResult) -> str:
    """Format a task result as plain text for display"""
    return TASK_RESULT_TEMPLATE.format(
        task_description=task_result.description, task_result=task_result.result
    )


def format_step_result_text(step_result: StepResult) -> str:
    """Format a step result as plain text for display"""
    tasks_str = "\n".join(
        f"  - {format_task_result_text(task)}" for task in step_result.task_results
    )
    return STEP_RESULT_TEMPLATE.format(
        step_description=step_result.step.description,
        step_result=step_result.result,
        tasks_str=tasks_str,
    )


def format_plan_result_text(plan_result: PlanResult) -> str:
    """Format the full plan execution state as plain text for display"""
    steps_str = (
        "\n\n".join(
            f"{i + 1}:\n{format_step_result_text(step)}"
            for i, step in enumerate(plan_result.step_results)
        )
        if plan_result.step_results
        else "No steps executed yet"
    )

    return PLAN_RESULT_TEMPLATE.format(
        plan_objective=plan_result.objective,
        steps_str=steps_str,
        plan_result=plan_result.result if plan_result.is_complete else "In Progress",
    )


def format_task_result_xml(task_result: TaskWithResult) -> str:
    """Format a task result with XML tags for better semantic understanding"""
    from mcp_agent.workflows.llm.prompt_utils import format_fastagent_tag
    
    # Include agent attribution if available
    agent_attr = ""
    if hasattr(task_result, "agent") and task_result.agent:
        agent_attr = f' agent="{task_result.agent}"'
    
    return format_fastagent_tag(
        "task-result", 
        f"\n<fastagent:description>{task_result.description}</fastagent:description>\n"
        f"<fastagent:result>{task_result.result}</fastagent:result>\n",
        {"description": task_result.description[:50] + "..." if len(task_result.description) > 50 else task_result.description}
    )


def format_step_result_xml(step_result: StepResult) -> str:
    """Format a step result with XML tags for better semantic understanding"""
    from mcp_agent.workflows.llm.prompt_utils import format_fastagent_tag
    
    # Format each task result with XML
    task_results = []
    for task in step_result.task_results:
        task_results.append(format_task_result_xml(task))
    
    # Combine task results
    task_results_str = "\n".join(task_results)
    
    # Build step result with metadata and tasks
    step_content = (
        f"<fastagent:description>{step_result.step.description}</fastagent:description>\n"
        f"<fastagent:summary>{step_result.result}</fastagent:summary>\n"
        f"<fastagent:task-results>\n{task_results_str}\n</fastagent:task-results>\n"
    )
    
    return format_fastagent_tag("step-result", step_content)


def format_plan_result(plan_result: PlanResult) -> str:
    """Format the full plan execution state with XML for better semantic understanding"""
    from mcp_agent.workflows.llm.prompt_utils import format_fastagent_tag
    
    # Format objective
    objective_tag = format_fastagent_tag("objective", plan_result.objective)
    
    # Format step results
    step_results = []
    for step in plan_result.step_results:
        step_results.append(format_step_result_xml(step))
    
    # Build progress section
    if step_results:
        steps_content = "\n".join(step_results)
        progress_content = (
            f"{objective_tag}\n"
            f"<fastagent:steps>\n{steps_content}\n</fastagent:steps>\n"
            f"<fastagent:status>{plan_result.result if plan_result.is_complete else 'In Progress'}</fastagent:status>\n"
        )
    else:
        # No steps executed yet
        progress_content = (
            f"{objective_tag}\n"
            f"<fastagent:steps>No steps executed yet</fastagent:steps>\n"
            f"<fastagent:status>Not Started</fastagent:status>\n"
        )
    
    return format_fastagent_tag("progress", progress_content)
