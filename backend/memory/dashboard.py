
from memory.semantic_memory import semantic_memory
def show_memory_dashboard(user_id):
    memories = semantic_memory.get_user_memories(
        user_id
    )

    print("\n========== MEMORY DASHBOARD ==========")
    print(f"User: {user_id}")

    documents = memories["documents"]
    metadatas = memories["metadatas"]
    ids = memories["ids"]

    print(f"Total memories: {len(ids)}")

    for i in range(len(ids)):
        print("\n--------------------------------------")
        print(f"ID: {ids[i]}")
        print(f"Memory: {documents[i]}")
        print(
            f"Access count: "
            f"{metadatas[i]['access_count']}"
        )
        print(
            f"Created: "
            f"{metadatas[i]['created_at']}"
        )