from unittest.mock import MagicMock, patch

from memory.consolidation import consolidate_memories


def test_consolidates_similar_memories():

    fake_memories = {
        "ids": [
            "mem_1",
            "mem_2",
            "mem_3",
        ],
        "documents": [
            "User prefers beginner-friendly explanations.",
            "User prefers explanations without unnecessary jargon.",
            "Vector RAG uses embeddings.",
        ],
    }

    fake_similar_results = {
        "mem_1": [
            {
                "id": "mem_1",
                "document": "User prefers beginner-friendly explanations.",
            },
            {
                "id": "mem_2",
                "document": "User prefers explanations without unnecessary jargon.",
            },
        ],

        "mem_2": [
            {
                "id": "mem_2",
                "document": "User prefers explanations without unnecessary jargon.",
            },
        ],

        "mem_3": [
            {
                "id": "mem_3",
                "document": "Vector RAG uses embeddings.",
            },
        ],
    }

    with patch(
        "memory.consolidation.semantic_memory"
    ) as mock_memory, patch(
        "memory.consolidation.consolidation_model"
    ) as mock_model:

        mock_memory.get_user_memories.return_value = (
            fake_memories
        )

        def fake_search(
            query,
            user_id,
            limit=3,
        ):
            for memory_id, document in zip(
                fake_memories["ids"],
                fake_memories["documents"],
            ):
                if document == query:
                    return fake_similar_results[
                        memory_id
                    ]

            return []

        mock_memory.search_with_ids.side_effect = (
            fake_search
        )

        decision = MagicMock()
        decision.should_consolidate = True
        decision.consolidated_memory = (
            "User prefers beginner-friendly "
            "explanations without unnecessary jargon."
        )

        mock_model.invoke.return_value = decision

        consolidate_memories("user_1")

        mock_memory.add_memory.assert_called_once_with(
            text=(
                "User prefers beginner-friendly "
                "explanations without unnecessary jargon."
            ),
            user_id="user_1",
            task_id="consolidated",
        )

        mock_memory.delete_memories.assert_any_call(
            "user_1",
            ["mem_2"],
        )

        mock_memory.delete_memories.assert_any_call(
            "user_1",
            ["mem_1"],
        )

def test_does_not_consolidate_unrelated_memories():

    fake_memories = {
        "ids": [
            "mem_1",
            "mem_2",
        ],
        "documents": [
            "Vector RAG uses embeddings.",
            "GraphRAG uses graph relationships.",
        ],
    }

    with patch(
        "memory.consolidation.semantic_memory"
    ) as mock_memory, patch(
        "memory.consolidation.consolidation_model"
    ) as mock_model:

        mock_memory.get_user_memories.return_value = (
            fake_memories
        )

        mock_memory.search_with_ids.return_value = [
            {
                "id": "mem_2",
                "document": (
                    "GraphRAG uses graph relationships."
                ),
            }
        ]

        decision = MagicMock()
        decision.should_consolidate = False
        decision.consolidated_memory = None

        mock_model.invoke.return_value = decision

        consolidate_memories("user_1")

        mock_memory.add_memory.assert_not_called()
        mock_memory.delete_memories.assert_not_called()