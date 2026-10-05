from state import AgentState
from langchain_ollama import ChatOllama
from models import ReviewResult
from llm import eval_llm
from tracing.helpers import trace_node


reviewer_model = eval_llm.with_structured_output(ReviewResult,  method="json_schema")

def reviewer_node(state: AgentState):
    """Review the specialist result."""
    prompt = f"""
        You are a reviewer agent.

        Original Task:
        {state['task']}

        Supervisor Plan:
        {state["subtasks"]}

        Specialist Outputs:
        {state["subtask_results"]}

        Rejected subtasks:
        {state.get("rejected_subtask_ids", [])}

        Important:
        - Subtasks listed in rejected_subtask_ids were intentionally rejected by the human.
        - Do not request those rejected subtasks to be retried.
        

        Review the completed specialist outputs against the original task
        and supervisor plan.

        Check:
        1. Correctness
        2. Relevance
        3. Completeness
        4. Clarity
        5. Whether each required subtask was actually completed
        6. Confidence as a decimal from 0 to 1
        7. Review score from 1 to 5

        Approval rules:
        - Approve only if the overall task is complete and ready for the user.
        - If any required subtask is incomplete, incorrect, missing, or needs
        revision, approved must be false.
        - If approved is false, return the IDs of every subtask that needs
        to be retried in failed_subtask_ids.
        - Only use subtask IDs that exist in the Supervisor Plan.
        - Do not invent subtask IDs.
        - If approved is true, failed_subtask_ids must be an empty list.
        - Explain what needs to be fixed in feedback.

        Example:
        If task_2 and task_3 need revision:
        failed_subtask_ids = ["task_2", "task_3"]

        If everything is acceptable:
        failed_subtask_ids = []
        """
    with trace_node(
        "agent.reviewer",
        state,
        agent_type="reviewer",
        prompt = prompt
    ) as (span, trace):

        response = reviewer_model.invoke(
            prompt
        )
        if response.failed_subtask_ids:
            span.set_attribute(
                "review.failed_subtasks",
                response.failed_subtask_ids
            )
        trace["summary"] = (
            f"Approved={response.approved}, "
            f"score={response.score}"
        )
        revision_count = state.get("revision_count", 0) + 1
        state["revision_count"] = revision_count
        return {
            "approved": response.approved,
            "review_feedback": response.feedback,
            "review_score": response.score,
            "revision_count": revision_count,
            "failed_subtask_ids": response.failed_subtask_ids,
            "confidnce_score": response.confidence
        }
