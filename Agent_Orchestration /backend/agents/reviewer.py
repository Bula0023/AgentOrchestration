from state import AgentState
from langchain_ollama import ChatOllama
from models import ReviewResult
from llm import eval_llm
from tracing.helpers import trace_node


reviewer_model = eval_llm.with_structured_output(ReviewResult,  method="json_schema")

def reviewer_node(state: AgentState):
    """Review the specialist result."""
    prompt = f"""
            You are a reviwer agent.
            
            Original Task:
            {state['task']}

            Supervisor Plan
            {state["subtasks"]}

            Specialist output:
            {state["subtask_results"]}

            Check:
            1. Correctness
            2. Revelvance
            3. Completeness
            4. Clarity
            5. Whether the task was actually completed
            6. confidence: decimal from 0 to 1
            7. Review score from 1-5
            Approve only if the output is ready for the user.
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
        if response.failed_subtask_id:
            span.set_attribute(
                "review.failed_subtask",
                response.failed_subtask_id
            )
        trace["summary"] = (
            f"Approved={response.approved}, "
            f"score={response.score}"
        )
        return {
            "approved": response.approved,
            "review_feedback": response.feedback,
            "review_score": response.score,
            "revision_count": state.get("revision_count", 0) + 1,
            "confidnce_score": response.confidence
        }
