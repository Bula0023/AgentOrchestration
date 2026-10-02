from state import AgentState
from langchain_ollama import ChatOllama
from models import SpecialistResult
from llm import llm
from memory.working_memory import memory
from tracing.helpers import trace_node

specialist_model = llm.with_structured_output(SpecialistResult,  method="json_schema", include_raw=True)

def writing_node(state: AgentState):
    """Writing specialist."""

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
            You are a writing specialist.

                Original task:
                {state["task"]}

                Assigned subtask:
                {subtask["description"]}

                Available tools:
                - file_write

                Important rules:

                - You cannot directly perform external actions.
                - You cannot claim that an email was sent, a file was deleted,
                a payment was made, or any other external action occurred
                unless the corresponding tool was actually executed successfully.

                - If the subtask requires a tool, set tool_name and tool_inputs.
                - Do not pretend the tool has already run.
                - For sensitive tools, only propose the action. Human approval
                will happen before execution.

                Complete only your assigned subtask.
                """
    with trace_node(
        "agent.writing",
        state,
        agent_type="writing",
        prompt=prompt
    ) as (span, trace):

        response = specialist_model.invoke(
            prompt
        )
        raw = response["raw"]
        response = response["parsed"]
        usage = raw.usage_metadata
        results = dict(state.get("subtask_results", {}))
        results[subtask["id"]] = response.result

        trace["summary"] = (
            "Completed writing subtask"
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
                "result": response.result,
            }
        )

        return {
            "subtask_results": results,
            "specialist_result": response.result,
            "sources": response.sources
        }