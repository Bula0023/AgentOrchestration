from enum import Enum


class ApprovalLevel(str, Enum):
    NOTIFY = "notify"
    APPROVE_ACTION = "approve_action"
    APPROVE_PLAN = "approve_plan"
    TAKE_OVER = "take_over"

def determine_approval_level(
        trigger: str
) -> ApprovalLevel:
    mapping = {
        "low_supervisor_confidence":
        ApprovalLevel.APPROVE_PLAN,

        "specialist_failed_twice":
        ApprovalLevel.TAKE_OVER,

        "financial_transaction":
        ApprovalLevel.APPROVE_ACTION,

        "data_deletion":
        ApprovalLevel.APPROVE_ACTION,

        "external_communication":
            ApprovalLevel.APPROVE_ACTION,

        "low_reviewer_score":
            ApprovalLevel.TAKE_OVER,

        "user_requested_human":
            ApprovalLevel.TAKE_OVER,
    }

    return mapping.get(
        trigger,
        ApprovalLevel.NOTIFY
    )