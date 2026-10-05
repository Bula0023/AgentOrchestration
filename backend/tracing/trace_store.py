import redis
import json
import os

class TraceStore:

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

    def _key(
        self,
        task_id: str,
    ) -> str:

        return f"trace:{task_id}"

    def add_node(
        self,
        task_id: str,
        node: dict,
    ):

        key = self._key(task_id)
        # Keep track of all task IDs
        self.redis.sadd(
            "trace_tasks",
            task_id,
        )

        self.redis.rpush(
            key,
            json.dumps(node),
        )

    def get_trace(
        self,
        task_id: str,
    ):

        key = self._key(task_id)

        nodes = self.redis.lrange(
            key,
            0,
            -1,
        )

        return [
            json.loads(node)
            for node in nodes
        ]


    def get_tasks(self):

        return list(
            self.redis.smembers(
                "trace_tasks"
            )
        )

    def get_all_trace_task_ids(self):
        task_ids = []

        for key in self.redis.scan_iter(
            match="trace:*"
        ):
            task_id = key.replace(
                "trace:",
                ""
            )

            task_ids.append(task_id)

        return task_ids
    def clear_trace(
        self,
        task_id: str,
    ):

        key = self._key(task_id)

        self.redis.delete(key)


trace_store = TraceStore()