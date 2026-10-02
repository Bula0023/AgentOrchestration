from routing.routes import (
    route_after_specialist,
    route_confidence,
    route_retry,
)

def test_specialist_success():
    state = {
        "specialist_success": True
    }

    result = route_after_specialist(state)

    assert result == "success"


def test_specialist_failure():
    state = {
        "specialist_success": False
    }

    result = route_after_specialist(state)

    assert result == "retry"

def test_high_confidence():
    state = {
        "specialist_confidence": 0.9
    }

    result = route_confidence(state)

    assert result == "continue"


def test_low_confidence():
    state = {
        "specialist_confidence": 0.3
    }

    result = route_confidence(state)

    assert result == "human"


def test_retry_allowed():
    state = {
        "retry_count": 1
    }

    result = route_retry(state)

    assert result == "retry"


def test_retry_limit_reached():
    state = {
        "retry_count": 2
    }

    result = route_retry(state)

    assert result == "human"