from memory.semantic_memory import semantic_memory


def get_memory_dashboard(user_id: str):

    memories = semantic_memory.get_user_memories(
        user_id
    )

    return {
        "user_id": user_id,
        "total_memories": len(
            memories["ids"]
        ),
        "memories": memories,
    }