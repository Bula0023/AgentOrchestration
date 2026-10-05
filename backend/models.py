from pydantic import BaseModel, Field
from typing import Literal
from tools.schemas import ( FileReadInput,
    FileReadOutput,
    WebSearchInput,
    WebSearchOutput,
    DatabaseQueryInput,
    DatabaseQueryOutput,
    APICallInput,
    APICallOutput,
    CodeExecutionInput, 
    CodeExecutionOutput,
    FileWriteInput,
    FileWriteOutput
)
# structured LLM outputs. This is where Pydantic models go

class Subtask(BaseModel):
    id: str = Field(description="unique subtask Id")

    description: str = Field(description="description of the subtask")

    specialist: Literal["research", "writing","code"] = Field(description="Specialist responsible of subtask")

    required_inputs: list[str] = Field(description="Inputs required to execute this subtask",
                                       default_factory=list)
    
    dependencies: list[str] = Field(default_factory=list, description="subtask ids that must be done before this subtask")

    expected_output_format: str = Field(description="Expected output format of subtask")

    complexity: Literal["low", "medium", "high"] = Field(
        description="Estimated difficulty of this subtask"
    )

class SpecialistResult(BaseModel):
    result: str
    success: bool = Field(description="Whether the specialist was able to complete the subtask successfully")

    confidence: float = Field(ge=0, le=1, description="Confidence level of the specialist in the result")
    error: str | None = None
    sources: list[str] = Field(default_factory=list)
    
    tool_name: str | None = None
    tool_inputs: (
    APICallInput
    | FileWriteInput
    | FileReadInput
    | WebSearchInput
    | DatabaseQueryInput
    | CodeExecutionInput
    | None
) = None

class ReviewResult(BaseModel):
    approved: bool
    feedback: str
    score: int = Field(ge=1,le=5)
    failed_subtask_ids: list[str]
    confidence: float = Field(ge=0, le=1, description="Confidence level of the reviewer in the result")

class SupervisorDecision(BaseModel):
    subtasks: list[Subtask] = Field(description="ordered execution plan for the user task")
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence that this plan can correctly complete the task"
    )

class MemoryExtraction(BaseModel):
    user_request: str

    execution_plan: list[str] = Field(
        default_factory=list
    )

    successful_approaches: list[str] = Field(
        default_factory=list
    )

    failed_approaches: list[str] = Field(
        default_factory=list
    )

    tools_used: list[str] = Field(
        default_factory=list
    )

    domain_facts: list[str] = Field(default_factory=list)

    user_preferences: list[str] = Field(
        default_factory=list
    )

class ConsolidationResult(BaseModel):
    should_consolidate:bool = Field(
        description="Whether these memories are redundant enough to merge"
    )

    consolidated_memory: str | None = Field(
        default= None,
        description="A summary preserving the important information from all memories"
    )

class SafetyClassification(BaseModel):
    sensitive: bool

    category: Literal[
        "financial_transaction",
        "data_deletion",
        "external_communication",
        "none"
    ]
    reason: str

class ApprovalRequest(BaseModel):
    approval_id: str
    task_id: str

    original_task: str

    plan: list[dict]

    completed_steps: dict[str, str]

    current_step: dict | None

    proposed_action: dict | None

    escalation_reason: str

    status: Literal[
        "pending",
        "approved",
        "rejected",
        "modified",
        "taken_over",
    ] = "pending"

    human_feedback: str | None = None


class HumanReviewRequest(BaseModel):
    requested: bool