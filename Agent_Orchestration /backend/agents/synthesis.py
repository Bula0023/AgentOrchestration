from state import AgentState
from llm import llm
from tracing.helpers import trace_node
def synthesis_node(state: AgentState):
    """Return thet reviewed result to the user"""
    prompt = f"""
            You are the supervisor agent.

            User task:
            {state["task"]}

            Approved specialist result:
            {state["specialist_result"]}

            Reviewer feedback:
            {state["review_feedback"]}

            Return the final answer to the user. Preserve the useful details,
            but remove internal workflow commentary.
            """
    with trace_node(
        "agent.synthesis",
        state,
        agent_type="research",
        prompt=prompt
    ) as (span, trace):
        final_answer = llm.invoke(
            prompt
        )
        # raw = response["raw"]
        # response = response["parsed"]
        response = final_answer
        usage = response.usage_metadata
        trace["response"] = response.content

        trace["decision"] = (
            "Completed research subtask"
        )
        span.set_attribute(
            "llm.input_tokens",
            usage.get("input_tokens", 0)
        )

        span.set_attribute(
            "llm.output_tokens",
            usage.get("output_tokens", 0)
        )
        return {
            "final_answer": final_answer.content
        }