import fakeredis
import pytest

from approval.approval_queue import ApprovalQueue
from models import ApprovalRequest


def make_queue():
    client = fakeredis.FakeRedis(
        decode_responses=True
    )

    return ApprovalQueue(
        client=client
    )


def make_request():
    return ApprovalRequest(
        approval_id="approval_123",
        task_id="task_123",
        original_task="Send an email",
        plan=[],
        completed_steps={},
        current_step={
            "id": "task_2",
            "description": "Send email",
            "specialist": "writing",
        },
        proposed_action={
            "tool_name": "send_email",
            "tool_inputs": {
                "to": "example@email.com",
                "subject": "Test email",
                "body": "Send email",
            },
        },
        escalation_reason=(
            "External communication"
        ),
    )

def test_enqueue_approval():

    queue = make_queue()

    request = make_request()

    queue.enqueue(request)

    pending = queue.get_pending()

    assert len(pending) == 1

    assert pending[0]["approval_id"] == (
        "approval_123"
    )

    assert pending[0]["status"] == "pending"

def test_reject_request():

    queue = make_queue()

    request = make_request()

    queue.enqueue(request)

    result = queue.reject(
        "approval_123",
        feedback="Do not send this."
    )

    assert result["current_step"]["status"] == "rejected"

    assert result["human_feedback"] == (
        "Do not send this."
    )

def test_modify_request():

    queue = make_queue()

    request = make_request()

    queue.enqueue(request)

    result = queue.modify(
        "approval_123",
        "Save email as draft instead"
    )

    assert result["current_step"]["status"] == "modified"

    assert result["modified_action"] == (
        "Save email as draft instead"
    )


def test_approve_unknown_request_fails():

    queue = make_queue()

    with pytest.raises(ValueError):
        queue.approve(
            "does_not_exist"
        )