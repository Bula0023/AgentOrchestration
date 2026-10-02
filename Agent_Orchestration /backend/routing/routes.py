from state import AgentState
from typing import Literal

def route_after_specialist(state: AgentState) -> Literal["success", "retry"]:
    if state["specialist_success"]:
        return "success"
    return "retry"

def route_retry(state: AgentState) -> Literal["retry", "human"]:
    if state.get("retry_count", 0) >= 2:
        return "human"
    return "retry"

def route_after_review(state: AgentState) -> Literal["approved", "revision", "human"]:
    if state["review_score"] <= 2 or state.get(
        "revision_count",
        0
    ) >= 3:
        return "human"
    if not state["approved"]:
        return "revision"
    
    return "approved"

def route_subtask(state:AgentState) -> Literal["research", "writing", "reviewer"]:
    subtask = state["current_subtask"]
    if subtask is None:
        return "reviewer"
    return subtask["specialist"]

def route_to_specialist(state: AgentState) -> Literal["research", "writing"]:
    return state["selected_specialist"]

# def route_after_review(state: AgentState) -> Literal["synthesis", "supervisor"]:
#     if state["review_score"] <= 2:
#         return "human"

#     if not state["approved"]:
#         return "revision"

#     return "approved"

def route_confidence(state: AgentState) -> Literal["continue", "human"]:
    if state["specialist_confidence"] < 0.7:
        return "human"
    return "continue"

def route_current_specialist(state: AgentState):
    return state["current_subtask"]["specialist"]

def route_after_supervisor(state: AgentState):
    if state["supervisor_confidence"] < 0.7:
        return "human"
    return "continue"

def route_sensitive_operation(state: AgentState):
    if state["sensitive_operation"]:
        return "human"

    return "continue"

def route_after_intake(state: AgentState):
    if state.get("user_requested_human", False):
        return "human"

    return "continue"

    
def route_after_human_review(state: AgentState):
    status = state["approval_status"]
    level = state["approval_level"]

    if status == "taken_over":
        return "take_over"

    if status == "rejected":
        return "rejected"

    if level == "approve_plan":
        return "plan_approved"

    if level == "approve_action":
        return "action_approved"

def route_escalation_level(state: AgentState):
    if state["approval_level"] == "notify" and state.get(
        "revision_count",
        0
    ) <= 2:
        return "continue"
    return "human_review"

def route_proposed_tool(state: AgentState):
    print("PROPOSED TOOL:", state.get("proposed_tool"))
    if state.get("proposed_tool"):
        return "tool"
    return "no_tool"