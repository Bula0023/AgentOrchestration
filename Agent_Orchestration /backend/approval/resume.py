from langgraph.types import interrupt
from state import AgentState
from tracing.helpers import trace_node

def human_approval_node(state: AgentState):
    with trace_node(
        "human.pause",
        state,
    ) as (span, trace):
        print("before interuption")
        decision = interrupt(
            {
                "approval_id": state["approval_id"],
                "task_id": state["task_id"],
                "reason": state.get(
                    "escalation_reason",
                    "Human approval required"
                ),
                "current_step": state.get("current_subtask"),
                "proposed_action": state.get("proposed_action"),
            }

        )
        print("after interruption")
        if (
            decision["status"] == "modified"
            and state["approval_level"] == "approve_plan"
        ):
            return {
                "subtasks": decision["modified_plan"],
                "approval_status": "modified",
                "needs_human": False,
            }

        if (
            decision["status"] == "modified"
            and state["approval_level"] == "approve_action"
        ):
            return {
                "modified_action": decision["modified_action"],
                "approval_status": "modified",
                "needs_human": False,
            }
        return {
            "approval_status": decision["status"],
            "human_feedback": decision.get("feedback"),
            "modified_action": decision.get("modified_action"),
            "needs_human": False,
        }

def human_takeover_node(state: AgentState):
    return {
        "final_answer": state["human_output"]
    }