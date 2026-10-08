
from unittest.mock import patch

from approval.escalation import prepare_escalation_node, ApprovalLevel

def test_prepare_escalation_creates_approval_request():

    state = {
        "task_id": "task_123",
        "task": "Send the customer an email",
        "subtasks": [
            {
                "id": "task_1",
                "description": "Draft email",
                "specialist": "writing",
                "dependencies": [],
            }
        ],
        "subtask_results": {
            "task_1": "Draft completed."
        },
        "current_subtask": {
            "id": "task_2",
            "description": "Send email",
            "specialist": "writing",
        },
        "proposed_action": {
            "tool_name": "send_email",
            "tool_inputs": {
                "to": "example@email.com",
                "subject": "Test email",
                "body": "Send email to customer",
            },
        },
        "sensitive_reason": (
            "External communication requires approval"
        ),
    }

    with patch(
    "approval.escalation.approval_queue"
    ) as mock_queue, patch(
        "approval.escalation.determine_approval_level",
        return_value=ApprovalLevel.TAKE_OVER,
    ):
        


        result = prepare_escalation_node(state)

        assert result["approval_status"] == "pending"
        assert result["needs_human"] is True

        assert result["approval_id"] is not None

        mock_queue.enqueue.assert_called_once()

        request = (
            mock_queue.enqueue.call_args.args[0]
        )

        assert request.task_id == "task_123"

        assert request.original_task == (
            "Send the customer an email"
        )

        assert request.completed_steps == {
            "task_1": "Draft completed."
        }

        assert request.proposed_action == {
                "tool_name": "send_email",
                "tool_inputs": {
                    "to": "example@email.com",
                    "subject": "Test email",
                    "body": "Send email to customer",
                },
            }
        

        assert request.escalation_reason == (
            "External communication requires approval"
        )