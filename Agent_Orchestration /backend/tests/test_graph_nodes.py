from graph import retry_specialist_node, save_result_node, select_next_subtask_node


def test_retry_count_increases():
    state = {
        "retry_count": 0
    }

    result = retry_specialist_node(state)

    assert result["retry_count"] == 1

def test_retry_count_increases_from_one():
    state = {
        "retry_count": 1
    }

    result = retry_specialist_node(state)

    assert result["retry_count"] == 2

def test_save_results():
    state = {
        "task_id": "test-123",
        "current_subtask_id": "task_2",
        "specialist_result": "Vector RAG uses embeddings.",
        "subtask_results": {
            "task_1": "RAG retrieves information."
        },
        "retry_count": 1,
    }

    result = save_result_node(state)

    assert result["subtask_results"]["task_1"] == (
        "RAG retrieves information."
    )

    assert result["subtask_results"]["task_2"] == (
        "Vector RAG uses embeddings."
    )

    assert result["current_subtask"] is None
    assert result["current_subtask_id"] is None
    assert result["retry_count"] == 0

def test_select_first_available_subtask():
    state = {
       "subtasks": [
        {
            "id": "task_1",
            "specialist": "research",
            "dependencies": [],
        },
        {
            "id": "task_2",
            "specialist": "writing",
            "dependencies": ["task_1"],
        },
        ],
        "subtask_results": {},
    }

    result = select_next_subtask_node(state)

    assert result["current_subtask_id"] == "task_1"

def test_select_subtask_after_dependency_finished():
    state = {
        "subtasks": [
            {
                "id": "task_1",
                "specialist": "research",
                "dependencies": [],
            },
            {
                "id": "task_2",
                "specialist": "writing",
                "dependencies": ["task_1"],
            },
        ],
        "subtask_results": {
            "task_1": "Finished research"
        },
    }

    result = select_next_subtask_node(state)

    assert result["current_subtask_id"] == "task_2"