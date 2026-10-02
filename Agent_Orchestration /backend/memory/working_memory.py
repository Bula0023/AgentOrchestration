import redis
import json
import os

class WorkingMemory:

    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv(
                "REDIS_HOST",
                "localhost"
            ),
            port=int(
                os.getenv(
                    "REDIS_PORT",
                    "6379"
                )
            ),
            db=0,
            decode_responses=True,
        )
    
    def _key(self, task_id: str):
        return f"task:{task_id}: memory"
    
    def save(self,task_id: str, field: str, value:list[dict]):
        key = self._key(task_id)

        self.redis.hset(
            key,
            field,
            json.dumps(value)
        )

    def get(self, task_id: str, field:str):
        key = self._key(task_id)
        value = self.redis.hget(
            key,
            field
        )
        if value is None:
            return None
        return json.loads(value)
    
    
    def clear(self, task_id:str):
        key = self._key(task_id)
        self.redis.delete(key)
    
    def add_error(self, task_id:str, error: str):
        errors = self.get(
        task_id,
        "errors"
        ) or []

        errors.append(error)

        self.save(
            task_id,
            "errors",
            errors
        )

memory = WorkingMemory()