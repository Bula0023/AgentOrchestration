from memory.semantic_memory import semantic_memory
from models import ConsolidationResult
from llm import llm

consolidation_model = llm.with_structured_output(
    ConsolidationResult
)

def consolidate_memories(user_id: str):
    memories = semantic_memory.get_user_memories(
        user_id
    )

    ids = memories["ids"]
    documents = memories["documents"]

    for memory_id, document in zip(ids, documents):

        similar = semantic_memory.search_with_ids(
            query=document,
            user_id=user_id,
            limit=3,
        )
        similar = [
            memory
            for memory in similar
            if memory["id"] != memory_id
        ]
        consolidated = False
        for candidate in similar:
            decision = consolidation_model.invoke(
                    f"""
                    Determine whether these long-term memories should
                    be consolidated.

                    Memory 1:
                    {document}

                    Memory 2:
                    {candidate["document"]}

                    Consolidate only when the memories are substantially
                    overlapping or redundant.

                    Do NOT consolidate merely because they discuss the
                    same general topic.

                    If consolidating, preserve all useful information.
                    Do not invent new facts.
                    """
                )
            if decision.should_consolidate:
                consolidated = True
                semantic_memory.add_memory(
                    text=decision.consolidated_memory,
                    user_id=user_id,
                    task_id="consolidated",
                )

                semantic_memory.delete_memories(
                    user_id,
                    [
                        candidate["id"]
                    ]
                )
                break
        if consolidated:
            semantic_memory.delete_memories(
                user_id,
                [memory_id]
            )
        