# from working_memory import WorkingMemory

# memory = WorkingMemory()

# memory.save(
#     "test-123",
#     "plan",
#     [
#         {
#             "id": "task_1",
#             "description": "Research Vector RAG"
#         },
#         {
#             "id": "task_2",
#             "description": "Research GraphRAG"
#         }
#     ]
# )

# plan = memory.get(
#     "test-123",
#     "plan"
# )

# print(plan)
from semantic_memory import SemanticMemory
memory = SemanticMemory()

memory.add_memory(
        "The user asked for a beginner-friendly explanation "
        "of Vector RAG and GraphRAG. Researching each approach "
        "separately before comparing them worked well."
    )

results = memory.search(
    "Explain RAG systems to a beginner"
)
print(results)
