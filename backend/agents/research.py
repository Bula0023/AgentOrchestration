from state import AgentState
from langchain_ollama import ChatOllama
from models import SpecialistResult
from llm import llm
from memory.working_memory import memory
from tracing.helpers import trace_node

specialist_model = llm.with_structured_output(SpecialistResult,  method="json_schema", include_raw=True,)

def research_node(state: AgentState):
    """Research specialist."""
    
    subtask = state["current_subtask"]
    completed_results = memory.get(
        state["task_id"],
        "subtask_results",
    ) or {}

    dependency_outputs = {
        dependency_id: completed_results[dependency_id]
        for dependency_id in subtask["dependencies"]
        if dependency_id in completed_results
    }
    prompt = f"""
            You are a research specialist.

            Original Task:
            {state['task']}

            Your assigned subtask:
            {subtask["description"]}

            Required inputs:
            {subtask["required_inputs"]}

            Results from dependency tasks:
            {dependency_outputs}

            Expected output format:
            {subtask["expected_output_format"]}

            Previous error if this is a retry:
            {state.get("specialist_error", "None")}

            Reviewer feedback if this is a revision:
            {state.get("review_feedback", "None")}

            Retry count:
            {state.get("retry_count", 0)}

            Complete only your assigned subtask.

            If this is a retry, use a different approach based on the previous error.

            If this is a revision, address the reviewer's feedback.
            Available tools:
            - file_read
            - web_search

            Return concise research notes.
            Maximum 200 words.
            Do not write the final user response.
            Do not invent sources.

            If completing the subtask requires a tool:
            - Set tool_name to the exact tool that should be used.
            - Set tool_inputs to the inputs required by that tool.
            - Do not claim the tool was executed.
            - Do not claim an external action happened unless the tool was actually executed.
            - If no tool is needed, set tool_name and tool_inputs to null.

            For sensitive external actions such as sending an email,
            only propose the action. Do not claim it was completed.
            """
    with trace_node(
        "agent.research",
        state,
        agent_type="research",
        prompt=prompt
    ) as (span, trace):

        response = specialist_model.invoke(
           prompt
        )
        raw = response["raw"]
        response = response["parsed"]
        # print("Research sepcialist response", response)
        usage = raw.usage_metadata
        trace["response"] = response.result

        trace["decision"] = (
            "Completed research subtask"
        )
        span.set_attribute(
            "specialist.confidence",
            response.confidence
        )

        span.set_attribute(
            "specialist.success",
            response.success
        )
        span.set_attribute(
        "llm.input_tokens",
            usage.get("input_tokens", 0)
        )

        span.set_attribute(
            "llm.output_tokens",
            usage.get("output_tokens", 0)
        )
        if response.tool_name:
            span.set_attribute(
                "tool.proposed",
                response.tool_name
            )
        memory.save(
            state["task_id"],
            "intermediate_results",
            {
                "subtask_id": state["current_subtask_id"],
                "result":  response.result,
            }
        )
        revision_count = state.get("revision_count", 0) + 1
        state["revision_count"] = revision_count
        return {
            "specialist_result": response.result,
            "sources": response.sources,
            "specialist_success": response.success,
            "specialist_confidence": response.confidence,

            "proposed_tool": response.tool_name,
            "proposed_tool_inputs": response.tool_inputs,
            "revision_count": revision_count,

            "proposed_action": {
                "tool_name": response.tool_name,
                "tool_inputs": response.tool_inputs,
            } if response.tool_name else None,
        }
