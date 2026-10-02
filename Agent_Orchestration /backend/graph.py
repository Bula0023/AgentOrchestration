from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import uuid

from state import AgentState
from langgraph.types import Command
from approval.actions import execute_approved_action_node
from agents.supervisor import supervisor_node
from agents.synthesis import synthesis_node
from agents.writing import writing_node
from agents.reviewer import reviewer_node
from agents.research import research_node
from agents.extract_memory import extract_memory_node
from approval.resume import human_approval_node, human_takeover_node
from approval.escalation import prepare_escalation_node, sensitive_operation_node
from memory.semantic_memory import semantic_memory
from tracing.helpers import trace_node


from routing.routes import (
    route_subtask,
    route_after_specialist,
    route_confidence,
    route_retry,
    route_current_specialist,
    route_after_review,
    route_after_supervisor,
    route_after_human_review,
    route_sensitive_operation,
    route_escalation_level,
    route_proposed_tool
)
from memory.working_memory import memory

def intake_node(state: AgentState):
    # task = state["task"].strip()
    # if not task:
    #     raise ValueError("Task cannot be empty.")
    task_id = str(uuid.uuid4())
    return {
        "task_id": task_id,
        "subtask_results": {},
        "retry_count": 0,
        "needs_human": False,
    }



def retry_specialist_node(state: AgentState):

    return {
        "retry_count": state.get("retry_count", 0) + 1,
    }

def retrieve_memory_node(state: AgentState):
    with trace_node(
        "memory.retrieve",
        state,
    ) as (span, trace):

        memories = semantic_memory.search(
            state["task"],
            user_id=state["user_id"],
            limit=3
        )
        span.set_attribute(
            "memory.result_count",
            len(memories)
        )

        span.set_attribute(
            "memory.used_for",
            "supervisor_planning"
        )
        print("\nRETRIEVED LONG-TERM MEMORY:")
        for memory in memories:
            print("-", memory)
        return {
            "relevant_memories": memories
        }



def select_next_subtask_node(state: AgentState):
    results= state.get("subtask_results", {})

    for subtask in state["subtasks"]:
        # completed
        if subtask["id"] in results:
            continue

        dependencies_done = all(
            dependency in results for dependency in subtask.get("dependencies", [])
        )
        if dependencies_done:
            return {
                "current_subtask": subtask,
                "current_subtask_id": subtask["id"],
            }
    return {}

def save_result_node(state: AgentState):
    """Save the specialist result and prepare for the next subtask or review"""

    results = dict(state.get("subtask_results", {}))
    results[state["current_subtask_id"]] = state["specialist_result"]

    memory.save(
        state["task_id"],
        "subtask_results",
        results
    )

    return{
        "subtask_results": results,
        "current_subtask": None,
        "current_subtask_id": None,
        "retry_count": 0,
        "specialist_result": None,
    }

def prepare_revision_node(state: AgentState):
    failed_id = state.get("failed_subtask_id")

    failed_subtask = next(
        task
        for task in state["subtasks"]
        if task["id"] == failed_id
    )
    results = dict(state["subtask_results"])
    results.pop(failed_id, None)
    return {
        "current_subtask": failed_subtask,
        "current_subtask_id": failed_id,
        "subtask_results": results,
        "retry_count": 0,
    }


def retry_router_node(state: AgentState):
    return {}

def proposed_tool_node(state: AgentState):
    return {}


def check_confidence_node(state: AgentState):
    return {}


def delivery_node(state: AgentState):
    print(state["final_answer"])
    memory.clear(
        state["task_id"]
    )
    return {}

def human_escalation_node(state: AgentState):
    reason = (
        state.get("specialist_error")
        or state.get("review_feedback")
        or "low confidence"
    )
    return {
        "needs_human": True,
        "escalation_reason": reason,
        "final_answer": (
            "Human review is required before",
            "this task can continue."
        ),
    }


def resume_graph(
        task_id: str,
        status: str,
        feedback: str | None = None,
        modified_action: str | None = None,
        modified_plan: list | None = None,
):
    config = {
    "configurable": {
        "thread_id": task_id
    }
    }
    print("here is the status", status)
    decision = {
        "status": status,
        "feedback": feedback,
        "modified_action": modified_action,
        "modified_plan": modified_plan,
        "needs_human": status == "escalation",  # Set needs_human if status is escalation
        "escalation_reason": "Human review is required before this task can continue."
            if status == "escalation" else None,
    }

    # if decision.get("needs_human"):
    #     print("Human escalation required. Pausing the graph.")
    #     return {
    #         "status": "paused",
    #         "reason": decision["escalation_reason"],
    #     }

    result = graph.invoke(
        Command(
            resume=decision
        ),
        config=config
    )
    print("Graph result:", result)
    return result



#build the graph
builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor_node)
builder.add_node("intake", intake_node)
builder.add_node("research", research_node)
builder.add_node("writing", writing_node)
builder.add_node("reviewer", reviewer_node)
builder.add_node("synthesis", synthesis_node)
builder.add_node("select_next_subtask", select_next_subtask_node)
builder.add_node("retry_specialist",retry_specialist_node)
builder.add_node("route_retry_specialist",retry_router_node)
builder.add_node("check_confidence", check_confidence_node)
builder.add_node("save_result",save_result_node)
builder.add_node("prepare_revision",prepare_revision_node)
# builder.add_node("human_escalation",human_escalation_node)
builder.add_node("proposed_tool", proposed_tool_node)
builder.add_node("extract_memory", extract_memory_node)
builder.add_node("delivery", delivery_node)
builder.add_node("retrieve_memory", retrieve_memory_node)
builder.add_node("human_approval",human_approval_node)
builder.add_node("prepare_escalation", prepare_escalation_node)
builder.add_node("sensitive_operation", sensitive_operation_node)
builder.add_node("execute_approved_action",execute_approved_action_node)
builder.add_node("human_takeover", human_takeover_node)

builder.add_edge(START, "intake")
builder.add_edge("intake", "retrieve_memory")
builder.add_edge("retrieve_memory","supervisor")
# builder.add_edge("supervisor", "select_next_subtask")
builder.add_edge("save_result","select_next_subtask")
# builder.add_edge("prepare_escalation","human_approval")
# builder.add_edge("human_escalation",END)

builder.add_edge("human_takeover", "delivery")
builder.add_edge("synthesis", "extract_memory")
builder.add_edge("extract_memory", "delivery")
builder.add_edge("delivery", END)

# builder.add_conditional_edges("supervisor", route_to_specialist,{"research": "research", "writing": "writing"},)
builder.add_conditional_edges(
    "route_retry_specialist",
    route_current_specialist,
    {
        "research": "research",
        "writing": "writing",
    },
)
builder.add_conditional_edges(
    "check_confidence",
    route_confidence,
    {
        "continue": "save_result",
        "human": "prepare_escalation",
    }
)
builder.add_conditional_edges(
    "retry_specialist", # after this node
    route_retry, # ask this function
    {
        "retry": "route_retry_specialist",# if it says retry
        "human": "prepare_escalation",# if it says human
    },
)
builder.add_conditional_edges(
    "select_next_subtask",
    route_subtask,
    {
        "research": "research",
        "writing": "writing",
        "reviewer": "reviewer",
    },
)
builder.add_conditional_edges(
    "research",
    route_after_specialist,
    {"success": "proposed_tool", "retry": "retry_specialist"}
)
builder.add_conditional_edges(
    "writing",
    route_after_specialist,
    {
        "success": "proposed_tool",
        "retry": "retry_specialist",
    },
)
builder.add_conditional_edges(
    "prepare_revision",
    route_current_specialist,
    {
        "research": "research",
        "writing": "writing",
    },
)

builder.add_conditional_edges(
    "reviewer", 
        route_after_review, 
        {"approved": "synthesis",
        "revision": "prepare_revision",
        "human": "prepare_escalation"})

builder.add_conditional_edges(
    "supervisor",
    route_after_supervisor,
    {
        "continue": "select_next_subtask",
        "human": "prepare_escalation",
    }
)
builder.add_conditional_edges(
    "sensitive_operation",
    route_sensitive_operation,
    {
        "human": "prepare_escalation",
        "continue": "select_next_subtask",
    },
)
builder.add_conditional_edges(
    "human_approval",
    route_after_human_review,
    {
        "plan_approved": "select_next_subtask",
        "action_approved": "execute_approved_action",
        "rejected": "supervisor",
        "take_over": "human_takeover",
    }
)

builder.add_conditional_edges(
    "prepare_escalation",
    route_escalation_level,
    {
        "continue": "select_next_subtask",
        "human_review": "human_approval",
    }
)

builder.add_conditional_edges(
    "proposed_tool",
    route_proposed_tool,
    {
        "tool": "sensitive_operation",
        "no_tool": "check_confidence",
    }
)
checkpointer = InMemorySaver()
graph = builder.compile(
    checkpointer=checkpointer
)
graph.get_graph().draw_mermaid_png(
    output_file_path="workflow.png"
)