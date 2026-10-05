from memory.working_memory import WorkingMemory

memory = WorkingMemory()


def test_memory():
    memory.save(
        "test-123",
        "plan",
        [
            {
                "id": "task_1",
                "description": "Research Vector RAG"
            },
            {
                "id": "task_2",
                "description": "Research GraphRAG"
            }
        ]
    )

    plan = memory.get(
        "test-123",
        "plan"
    )

    assert plan == [{'id': 'task_1', 'description': 'Research Vector RAG'}, {'id': 'task_2', 'description': 'Research GraphRAG'}]

def test_memory_deletion():
    memory.clear("test-123")
    value =  memory.get(
        "test-123",
        "plan"
    )

    assert value == None