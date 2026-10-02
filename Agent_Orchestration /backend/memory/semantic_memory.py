import chromadb
import uuid
import time
import uuid

class SemanticMemory:

    def __init__(self, path="./chroma_data"):
        self.client = chromadb.PersistentClient(
            path="./chroma_data"
        )
        self.collection = (
            self.client.get_or_create_collection(
                name="agent_memory"
            )
        )
    
    def add_memory(self,text:str,user_id:str,task_id:str):
        memory_id = str(uuid.uuid4())

        self.collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[{
            "user_id": user_id,
            "task_id": task_id,
            "access_count": 0,
            "created_at": time.time(),
            "last_accessed": time.time(),
        }],
        )
        return memory_id
    
    def is_stale(metadata):
        age_seconds = (
            time.time() - metadata["last_accessed"]
        )
        thirty_days = 30 * 24 * 60 * 60

        return (
        age_seconds > thirty_days
        and metadata["access_count"] < 2
        )
    
    def get_user_memories(self, user_id: str):
        return self.collection.get(
            where={"user_id": user_id}
        )


    def delete_user_memories(self, user_id: str):
        self.collection.delete(
            where={"user_id": user_id}
        )

    def delete_memories(self,user_id: str, memory_ids: list[str]):
        self.collection.delete(
            ids=memory_ids,
            where={"user_id": user_id}
        )

    
    def search(self,query:str, user_id:str, limit:int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={
            "user_id": user_id
        },
        )
        if not results["documents"]:
            return []
        ids = results["ids"][0]
        for memory_id in ids:
            memory = self.collection.get(
                ids=[memory_id]
            )
            metadata = memory["metadatas"][0]

            metadata["access_count"] += 1
            metadata["last_accessed"] = time.time()
            self.collection.update(
                ids=[memory_id],
                metadatas=[metadata],
            )
        return results["documents"][0]
    
    def search_with_ids(
        self,
        query: str,
        user_id: str,
        limit: int = 3,
    ):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"user_id": user_id},
        )

        if not results["documents"]:
            return []

        return [
            {
                "id": memory_id,
                "document": document,
                "distance": distance,
            }
            for memory_id, document, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]


semantic_memory = SemanticMemory()

# decay idea importance = access_count / (1 + age_in_days)