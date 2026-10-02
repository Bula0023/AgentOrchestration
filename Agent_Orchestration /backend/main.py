import os 
from typing import Literal, Callable, Type
# from typing_extensions import TypedDict
from models import ApprovalRequest
from approval.approval_queue import approval_queue
from graph import graph
from fastapi import FastAPI, Body,  Header, BackgroundTasks
from approval.approval_queue import approval_queue
from graph import resume_graph
from fastapi.middleware.cors import CORSMiddleware
from tracing.trace_store import trace_store
from tracing.telemetry import tracer
import uuid
from fastapi.responses import JSONResponse
import traceback



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/traces")
def get_traces():

   return {
        "tasks":
            trace_store.get_all_trace_task_ids()
    }

@app.get("/traces/{task_id}")
def get_trace(
    task_id: str
):
    
    nodes = (
        trace_store.get_trace(
            task_id
        )
    )

    return {
        "task_id":
            task_id,

        "nodes":
            nodes,
    }

def run_graph(
    task_id: str,
    task: str
):
    config = {
        "configurable": {
            "thread_id": task_id
        }
    }

    with tracer.start_as_current_span(
        "task.execution"
    ) as root_span:

        root_span.set_attribute(
            "task.id",
            task_id
        )

        root_span.set_attribute(
            "user.id",
            "test_user_1"
        )

        graph.invoke(
            {
                "task_id": task_id,
                "user_id": "test_user_1",
                "task": task,
                "revision_count": 0,
            },
            config=config
        )


@app.post("/tasks")
def submit_task(
    task: str,
    background_tasks: BackgroundTasks,
):

    task_id = str(uuid.uuid4())

    background_tasks.add_task(
        run_graph,
        task_id,
        task
    )

    return {
        "task_id": task_id,
        "status": "running"
    }
@app.get("/approvals")
def get_approvals():
    return approval_queue.get_pending()

@app.post("/approvals/{approval_id}/approve")
def approve_request(approval_id: str):
    try:
        approval = approval_queue.approve(approval_id)
        return resume_graph(
            task_id=approval["task_id"],
            status="approved",
        )
    except ValueError as e:
        print("Error:", str(e))
        return JSONResponse(
            status_code=404,
            content={"error": str(e)},
        )

@app.post("/approvals/{approval_id}/reject")
def reject_request(approval_id: str):
    try:
        approval = approval_queue.reject(
            approval_id
        )

        return resume_graph(
            approval=approval
        )
    except ValueError as e:
        print("Error:", str(e))
        return JSONResponse(
            status_code=404,
            content={"error": str(e)},
        )

@app.delete("/traces/{task_id}")
def delete_trace(task_id: str):

    try:
        deleted = trace_store.clear_trace(
            task_id
        )

        return {
            "message": "Trace deleted",
            "task_id": task_id,
            "deleted": deleted,
        }

    except Exception as e:

        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "details": str(e),
            },
        )

@app.post("/approvals/{approval_id}/modify")
def modify_request(
    approval_id: str,
    modified_action: str,
):
    try:
        approval = approval_queue.modify(
            approval_id,
            modified_action,
        )

        return resume_graph(
            task_id=approval["task_id"],
            status="modified",
            modified_action=modified_action,
        )
    except ValueError as e:
        print("Error:", str(e))
        return JSONResponse(
            status_code=404,
            content={"error": str(e)},
        )


def main():
    task_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": task_id
        }
    }
        
    with tracer.start_as_current_span(
        "task.execution"
    ) as root_span:

        # root_span.set_attribute(
        #     "task.id",
        #     task_id
        # )

        root_span.set_attribute(
            "user.id",
            "test_user_1"
        )

        result = graph.invoke(
            {
                "task_id": task_id,
                "user_id": "test_user_1",
                "task": (
                    # "Explain the difference between vector RAG and GraphRAG "
                    # "for a beginner."
                    # "Explain hybrid RAG for a beginner."""
                #    "Research the latest major differences between Vector RAG and GraphRAG, write a short summary, save the summary to a file, and then email it to test@example.com." 
                    "How does rag work and email taht to horoomb@gmail.com"
                ),
                "revision_count": 0,
            },
            config=config
        )
        # print(result)
        print("SUBTASKS VALUE:", result.get("subtasks"))
        print("SUBTASKS LENGTH:", len(result.get("subtasks", [])))
        print("\nPLAN:")
        for step in result["subtasks"]:
            f"- {step['id']}: {step['description']} "
            f"({step['specialist']})"

        print("\nREVIEW SCORE:", result["review_score"])
        print("\nFINAL ANSWER:")
        print(result["final_answer"])

    
if __name__ == "__main__":
    main()