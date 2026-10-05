from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

class TestState(TypedDict):
    task_id: str
    approval_status: str | None
    modified_action: str | None
    final_answer: str | None

def approval_node(state: TestState):

    decision = interrupt(
        {
            "message": "Approve this test?",
            "task_id": state["task_id"],
        }
    )

    print("RESUMED WITH:", decision)

    return {
        "approval_status":
            decision["status"],

        "modified_action":
            decision.get(
                "modified_action"
            ),
    }

def final_node(state: TestState):

    if (
        state["approval_status"]
        == "modified"
    ):

        return {
            "final_answer":
                f"Modified action: "
                f"{state['modified_action']}"
        }

    return {
        "final_answer":
            f"Finished with status: "
            f"{state['approval_status']}"
    }


builder = StateGraph(TestState)

builder.add_node(
    "approval",
    approval_node
)

builder.add_node(
    "final",
    final_node
)

builder.add_edge(
    START,
    "approval"
)

builder.add_edge(
    "approval",
    "final"
)

builder.add_edge(
    "final",
    END
)


checkpointer = InMemorySaver()

test_graph = builder.compile(
    checkpointer=checkpointer
)

task_id = "human-test-1"

config = {
    "configurable": {
        "thread_id": task_id
    }
}


result = test_graph.invoke(
    {
        "task_id": task_id,
        "approval_status": None,
        "final_answer": None,
    },
    config=config
)

print("FIRST RESULT:")
print(result)
result = test_graph.invoke(
    Command(
        resume={
            "status": "approved"
        }
    ),
    config=config
)

print("RESUMED RESULT:")
print(result)

def run_approval_test(
    thread_id: str,
    decision: dict,
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print("\nSTARTING:")
    print(thread_id)

    first_result = test_graph.invoke(
        {
            "task_id": thread_id,
            "approval_status": None,
            "final_answer": None,
        },
        config=config
    )

    print("PAUSED RESULT:")
    print(first_result)

    resumed_result = test_graph.invoke(
        Command(
            resume=decision
        ),
        config=config
    )

    print("RESUMED RESULT:")
    print(resumed_result)

    return resumed_result

run_approval_test(
    "human-test-approve",
    {
        "status": "approved"
    }
)

run_approval_test(
    "human-test-reject",
    {
        "status": "rejected"
    }
)
run_approval_test(
    "human-test-modify",
    {
        "status": "modified",
        "modified_action":
            "Use the updated action"
    }
)