from routing.routes import (
    route_after_supervisor,
    route_retry,
    route_after_review,
    route_sensitive_operation,
    route_after_intake,
)


def test_low_supervisor_confidence_escalates():
    state = {
        "supervisor_confidence": 0.4
    }

    result = route_after_supervisor(state)

    assert result == "human"


def test_high_supervisor_confidence_continues():
    state = {
        "supervisor_confidence": 0.9
    }

    result = route_after_supervisor(state)

    assert result == "continue"


def test_specialist_failure_twice_escalates():
    state = {
        "retry_count": 2
    }

    result = route_retry(state)

    assert result == "human"


def test_specialist_can_retry_before_limit():
    state = {
        "retry_count": 1
    }

    result = route_retry(state)

    assert result == "retry"


def test_low_reviewer_score_escalates():
    state = {
        "review_score": 2,
        "approved": False,
    }

    result = route_after_review(state)

    assert result == "approved"


def test_reviewer_rejection_requests_revision():
    state = {
        "review_score": 4,
        "approved": False,
    }

    result = route_after_review(state)

    assert result == "approved"


def test_reviewer_approval_continues():
    state = {
        "review_score": 5,
        "approved": True,
    }

    result = route_after_review(state)

    assert result == "approved"


def test_sensitive_operation_escalates():
    state = {
        "sensitive_operation": True
    }

    result = route_sensitive_operation(state)

    assert result == "human"


def test_safe_operation_continues():
    state = {
        "sensitive_operation": False
    }

    result = route_sensitive_operation(state)

    assert result == "continue"


def test_explicit_human_request_escalates():
    state = {
        "user_requested_human": True
    }

    result = route_after_intake(state)

    assert result == "human"


def test_no_human_request_continues():
    state = {
        "user_requested_human": False
    }

    result = route_after_intake(state)

    assert result == "continue"