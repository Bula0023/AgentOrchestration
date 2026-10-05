from state import AgentState
from tools.tool_registry import registry

def execute_approved_action_node(state: AgentState):
    action = (
        state.get("modified_action")
        or state.get("proposed_action")
    )
    tool_name = action["tool_name"]
    tool_inputs = action["inputs"]

    result = registry.execute(
        tool_name=tool_name,
        specialist=action["specialist"],
        inputs=tool_inputs,
    )
    return {
        "action_result": result.model_dump(),
        "approval_status": None,
        "approval_id": None,
    }