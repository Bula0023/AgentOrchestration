from fastapi.testclient import TestClient

from main import app


from typing_extensions import TypedDict
from unittest.mock import patch

from graph import resume_graph
from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from langgraph.types import (
    interrupt,
    Command,
)
client = TestClient(app)

class TestState(TypedDict, total=False):
    task_id: str
    approval_status: str
    human_feedback: str | None
    finished: bool

def approval_node(state: TestState):

    decision = interrupt(
        {
            "task_id": state["task_id"],
            "message": "Approval required",
        }
    )

    return {
        "approval_status": decision["status"],
        "human_feedback": decision.get(
            "feedback"
        ),
    }

def finish_node(state: TestState):

    return {
        "finished": True
    }

def route_decision(state: TestState):

    if state["approval_status"] == "approved":
        return "continue"

    return "stop"

def create_test_graph():

    builder = StateGraph(TestState)

    builder.add_node(
        "approval",
        approval_node
    )

    builder.add_node(
        "finish",
        finish_node
    )

    builder.add_edge(
        START,
        "approval"
    )

    builder.add_conditional_edges(
        "approval",
        route_decision,
        {
            "continue": "finish",
            "stop": END,
        }
    )

    builder.add_edge(
        "finish",
        END
    )

    return builder.compile(
        checkpointer=InMemorySaver()
    )

def test_graph_pauses_for_human():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "task_123"
        }
    }

    result = graph.invoke(
        {
            "task_id": "task_123"
        },
        config=config,
    )

    assert "__interrupt__" in result

    assert result["finished"] if "finished" in result else True

def test_graph_pauses_for_human():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "task_123"
        }
    }

    result = graph.invoke(
        {
            "task_id": "task_123"
        },
        config=config,
    )

    assert "__interrupt__" in result
    assert "finished" not in result

def test_approve_resumes_graph():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "task_123"
        }
    }

    first_result = graph.invoke(
        {
            "task_id": "task_123"
        },
        config=config,
    )

    assert "__interrupt__" in first_result

    resumed = graph.invoke(
        Command(
            resume={
                "status": "approved"
            }
        ),
        config=config,
    )

    assert resumed["approval_status"] == (
        "approved"
    )

    assert resumed["finished"] is True

def test_reject_does_not_continue():

    graph = create_test_graph()

    config = {
        "configurable": {
            "thread_id": "task_456"
        }
    }

    result = graph.invoke(
        {
            "task_id": "task_456"
        },
        config=config,
    )

    assert "__interrupt__" in result

    resumed = graph.invoke(
        Command(
            resume={
                "status": "rejected",
                "feedback": (
                    "Do not perform this action"
                ),
            }
        ),
        config=config,
    )

    assert resumed["approval_status"] == (
        "rejected"
    )

    assert resumed["human_feedback"] == (
        "Do not perform this action"
    )

    assert "finished" not in resumed

def test_resume_graph_uses_same_thread_id():

    with patch(
        "graph.graph.invoke"
    ) as mock_invoke:

        mock_invoke.return_value = {
            "approval_status": "approved"
        }

        result = resume_graph(
            task_id="task_123",
            status="approved",
        )

        assert result[
            "approval_status"
        ] == "approved"

        mock_invoke.assert_called_once()

        args, kwargs = (
            mock_invoke.call_args
        )

        config = kwargs["config"]

        assert (
            config["configurable"]["thread_id"]
            == "task_123"
        )

def test_approve_endpoint():

    with patch(
        "main.approval_queue.approve"
    ) as mock_approve, patch(
        "main.resume_graph"
    ) as mock_resume:

        mock_approve.return_value = {
            "approval_id": "approval_123",
            "task_id": "task_123",
            "status": "approved",
        }

        mock_resume.return_value = {
            "status": "completed"
        }

        response = client.post(
            "/approvals/approval_123/approve"
        )

        assert response.status_code == 200

        mock_approve.assert_called_once_with(
            "approval_123"
        )

        mock_resume.assert_called_once()