from models import SafetyClassification, ApprovalRequest
from state import AgentState
from approval.approval_queue import approval_queue
from llm import llm
from enum import Enum
import uuid
from tracing.helpers import trace_node
from .levels import determine_approval_level

safety_model = llm.with_structured_output(SafetyClassification)
class ApprovalLevel(str, Enum):
    NOTIFY = "notify"
    APPROVE_ACTION = "approve_action"
    APPROVE_PLAN = "approve_plan"
    TAKE_OVER = "take_over"

TOOL_APPROVAL_LEVELS = {
    "send_email": "approve_action",
    "send_slack_message": "approve_action",
    "delete_file": "approve_action",
    "delete_user_data": "approve_action",
    "make_payment": "approve_action",
    "transfer_money": "approve_action",
}

def sensitive_operation_node(state: AgentState):

    proposed_tool = state.get("proposed_tool")
    if isinstance(proposed_tool, dict):
        proposed_tool = proposed_tool.get("tool_name")
    if proposed_tool in TOOL_APPROVAL_LEVELS:
        return {
            "sensitive_operation": True,
            "sensitive_reason": (
                f"Tool '{proposed_tool}' requires human approval."
            ),
            "approval_level": TOOL_APPROVAL_LEVELS[proposed_tool],
        }

    response = safety_model.invoke(

        f"""
        Determine whether the proposed action requires
        human approval.

        Original task:
        {state["task"]}

        Current subtask:
        {state["current_subtask"]}

        Proposed tool:
        {state.get("proposed_tool")}

        Proposed tool inputs:
        {state.get("proposed_tool_inputs")}

        Proposed action:
        {state.get("proposed_action")}

        Escalate if the action involves:
        - a financial transaction
        - deletion of user or external data
        - sending external communications

        Classify only the proposed action.
        """
    )
    
    return {
        "sensitive_operation":
            response.sensitive,

        "sensitive_reason":
            response.reason,

        "approval_level":
            "approve_action"
            if response.sensitive
            else None,
    }

def prepare_escalation_node(state: AgentState):
    
    approval_id = str(uuid.uuid4())

    with trace_node(
        "prepare.escalation",
        state,
    ) as (span, trace):

        escalation_reason = (
            state.get("sensitive_reason")
            or state.get("specialist_error")
            or state.get("review_feedback")
            or "Human review requested"
        )

        approval_level = determine_approval_level(
            escalation_reason
        )

        request = ApprovalRequest(
            approval_id=approval_id,
            task_id=state["task_id"],
            original_task=state["task"],
            plan=state["subtasks"],
            completed_steps=state.get(
                "subtask_results",
                {}
            ),
            current_step=state.get(
                "current_subtask"
            ),
            proposed_action=state.get(
                "proposed_action"
            ),
            escalation_reason=escalation_reason,
            approval_level=approval_level,
            
        )

        span.set_attribute(
            "trace.status",
            "escalated"
        )

        span.set_attribute(
            "approval.level",
            approval_level.value
        )

        span.set_attribute(
            "approval.reason",
            escalation_reason
        )

        trace["status"] = "escalated"

        trace["summary"] = (
            f"Human approval requested: "
            f"{escalation_reason}"
        )
        if state.get(
        "revision_count",
            0
        ) > 2:
            approval_queue.enqueue(request)

        return {
            "needs_human": True,
            "approval_id": approval_id,
            "approval_status": "pending",
            "approval_level": approval_level.value,
            "escalation_reason": escalation_reason,
        }