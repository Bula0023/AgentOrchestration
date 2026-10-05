from memory.semantic_memory import SemanticMemory
import uuid

# memory = SemanticMemory()
def test_added_memory(tmp_path):
    memory = SemanticMemory(
        path=str(tmp_path)
    )
    text = ("The user asked for a beginner-friendly explanation "
        "of Vector RAG and GraphRAG. Researching each approach "
        "separately before comparing them worked well."
    )
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    memory.add_memory(text,user_id, task_id)
        

    results = memory.search(
        "Explain RAG systems to a beginner",
        user_id
    )
    print(results)

    assert text in results
