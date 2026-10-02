from approval.levels import (
    ApprovalLevel,
    determine_approval_level,
)
from routing.routes import route_after_human_review, route_escalation_level

from unittest.mock import patch

from approval.resume import human_approval_node

def test_low_supervisor_confidence_requires_plan_approval():
    result = determine_approval_level(
        "low_supervisor_confidence"
    )

    assert result == ApprovalLevel.APPROVE_PLAN


def test_sensitive_action_requires_action_approval():
    result = determine_approval_level(
        "external_communication"
    )

    assert result == ApprovalLevel.APPROVE_ACTION


def test_data_deletion_requires_action_approval():
    result = determine_approval_level(
        "data_deletion"
    )

    assert result == ApprovalLevel.APPROVE_ACTION


def test_specialist_failure_twice_requires_takeover():
    result = determine_approval_level(
        "specialist_failed_twice"
    )

    assert result == ApprovalLevel.TAKE_OVER


def test_low_reviewer_score_requires_takeover():
    result = determine_approval_level(
        "low_reviewer_score"
    )

    assert result == ApprovalLevel.TAKE_OVER


def test_unknown_trigger_defaults_to_notify():
    result = determine_approval_level(
        "minor_nonblocking_issue"
    )

    assert result == ApprovalLevel.NOTIFY


def test_notify_does_not_pause():
    state = {
        "approval_level": ApprovalLevel.NOTIFY
    }

    assert route_escalation_level(state) == "continue"


def test_approve_plan_goes_to_human_review():
    state = {
        "approval_level": ApprovalLevel.APPROVE_PLAN
    }

    assert route_escalation_level(state) == "human_review"


def test_approve_action_goes_to_human_review():
    state = {
        "approval_level": ApprovalLevel.APPROVE_ACTION
    }

    assert route_escalation_level(state) == "human_review"


def test_takeover_goes_to_human_review():
    state = {
        "approval_level": ApprovalLevel.TAKE_OVER
    }

    assert route_escalation_level(state) == "human_review"



def test_approved_plan_goes_to_subtask_execution():
    state = {
        "approval_status": "approved",
        "approval_level": "approve_plan",
    }

    assert (
        route_after_human_review(state)
        == "plan_approved"
    )


def test_modified_plan_also_goes_to_subtask_execution():
    state = {
        "approval_status": "modified",
        "approval_level": "approve_plan",
    }

    assert (
        route_after_human_review(state)
        == "plan_approved"
    )


def test_approved_action_goes_to_action_execution():
    state = {
        "approval_status": "approved",
        "approval_level": "approve_action",
    }

    assert (
        route_after_human_review(state)
        == "action_approved"
    )


def test_modified_action_goes_to_action_execution():
    state = {
        "approval_status": "modified",
        "approval_level": "approve_action",
    }

    assert (
        route_after_human_review(state)
        == "action_approved"
    )


def test_rejected_approval_replans():
    state = {
        "approval_status": "rejected",
        "approval_level": "approve_plan",
    }

    assert (
        route_after_human_review(state)
        == "rejected"
    )


def test_takeover_routes_to_human_takeover():
    state = {
        "approval_status": "taken_over",
        "approval_level": "take_over",
    }

    assert (
        route_after_human_review(state)
        == "take_over"
    )



def test_modified_plan_replaces_subtasks():

    state = {
        "approval_id": "approval_1",
        "approval_level": "approve_plan",
        "task_id": "task_1",
        "subtasks": [
            {
                "id": "task_1",
                "description": "Old plan"
            }
        ],
        "proposed_action": None,
        "escalation_reason": (
        "Supervisor confidence in the execution plan was below the approval threshold."
    ),
    }

    fake_decision = {
        "status": "modified",
        "modified_plan": [
            {
                "id": "task_1",
                "description": "New plan"
            }
        ]
    }

    with patch(
        "approval.resume.interrupt",
        return_value=fake_decision,
    ):

        result = human_approval_node(state)

    assert result["approval_status"] == "modified"

    assert result["subtasks"] == [
        {
            "id": "task_1",
            "description": "New plan"
        }
    ]

    assert result["needs_human"] is False

def test_modified_action_updates_action():

    state = {
        "approval_id": "approval_2",
        "approval_level": "approve_action",
        "task_id": "task_2",
        "subtasks": [],
        "proposed_action": "Send email",
        "escalation_reason": (
        "The proposed action requires human approval before execution."
    ),
    }

    fake_decision = {
        "status": "modified",
        "modified_action": "Save as draft",
    }

    with patch(
        "approval.resume.interrupt",
        return_value=fake_decision,
    ):

        result = human_approval_node(state)

    assert result["approval_status"] == "modified"

    assert result["modified_action"] == (
        "Save as draft"
    )

    assert result["needs_human"] is False