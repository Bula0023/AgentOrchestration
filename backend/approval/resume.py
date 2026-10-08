from langgraph.types import interrupt
from state import AgentState
from tracing.helpers import trace_node
# This node is called when there is a human 
def human_approval_node(state: AgentState):
    
    with trace_node(
        "human.pause",
        state,
    ) as (span, trace):

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
        trace["decision"] = decision

        span.set_attribute(
            "approval.status",
            decision["status"]
        )


        span.set_attribute(
            "approval.feedback",
            decision.get("feedback","")
        )
        print("after interruption")
        if decision["status"] == "rejected":
            rejected_ids = list(
                state.get("rejected_subtask_ids", [])
            )

            current_id = state.get("current_subtask_id")

            if current_id and current_id not in rejected_ids:
                rejected_ids.append(current_id)

            return {
                "approval_status": "rejected",
                "human_feedback": decision.get("feedback"),
                "needs_human": False,
                "rejected_subtask_ids": rejected_ids,
            }
        
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
        if decision["status"] == "approved":
            completed_ids = list(
                state.get("subtask_results", {}).keys()
            )

            current_id = state.get("current_subtask_id")

            if current_id and current_id not in completed_ids:
                completed_ids.append(current_id)

            return {
                "approval_status": "approved",
                "needs_human": False,
                "completed_subtask_ids": completed_ids,
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