import json
import redis
from models import ApprovalRequest
import os

class ApprovalQueue:

    def __init__(self, client=None):

        self.client = client or redis.Redis(
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
            decode_responses=True
        )
    
    def enqueue(self,request: ApprovalRequest):
        key = f"approval:{request.approval_id}"

        self.client.set(
            key,
            request.model_dump_json()
        )

        self.client.rpush(
            "approval_queue",
            request.approval_id
        )

    def get_pending(self):
        approval_ids = self.client.lrange(
            "approval_queue",
            0,
            -1
        )

        requests = []
        for approval_id in approval_ids:

            data = self.client.get(
                f"approval:{approval_id}"
            )

            if data:
                requests.append(
                    json.loads(data)
                )

        return requests
    
    def approve(self, approval_id):
        key = f"approval:{approval_id}"

        data = self.client.get(key)

        if data is None:
            raise ValueError("Approval request not found")
        
        request = json.loads(data)

        request["status"] = "approved"

        self.client.set(
            key,
            json.dumps(request)
        )
        
        return request

    def reject(self, approval_id: str, feedback:str):
        key = f"approval:{approval_id}"

        data = self.client.get(key)

        if data is None:
            raise ValueError("Approval request not found")
        
        request = json.loads(data)

        request["status"] = "rejected"
        request["human_feedback"] = feedback

        self.client.set(
            key,
            json.dumps(request)
        )

        return request
    
    def modify(self,approval_id: str, modified_action: str):
        key = f"approval:{approval_id}"

        data = self.client.get(key)

        if data is None:
            raise ValueError("Approval request not found")
        
        request = json.loads(data)

        request["status"] = "modified"
        request["modified_action"] = modified_action

        self.client.set(
            key,
            json.dumps(request)
        )

        return request
        

    
approval_queue = ApprovalQueue()
