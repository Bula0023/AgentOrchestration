from typing_extensions import TypedDict
from models import Subtask

class AgentState(TypedDict, total=False):
    user_id: str
    #Intake
    task:str
    task_id:str
    #planning
    subtasks: list[Subtask]
    #Execution
    current_subtask: dict | None
    current_subtask_id: str | None
    subtask_results: dict[str, str]
    relevant_memories: list[str]
   

    specialist_result: str
    specialist_success: bool
    specialist_confidence: float
    sources: list[str]
    #Retry
    retry_count: int

    #Review
    approved: bool
    review_feedback:str
    review_score: int

    revision_count: int
    #Human escalation
    supervisor_confidence: float

    sensitive_operation: bool
    sensitive_reason: str | None

    user_requested_human: bool

    needs_human: bool
    escalation_reason: str | None

    proposed_action: dict | None

    approval_id: str | None
    approval_level: str | None
    approval_status: str | None
    human_feedback: str | None
    modified_action: str | None
    human_output: str | None
    review_retry: int | None
    rejected_subtask_ids: list[str]
    #tools
    proposed_tool: str | None
    proposed_tool_inputs: dict | None
    #final
    final_answer: str

