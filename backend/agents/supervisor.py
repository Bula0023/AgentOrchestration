from state import AgentState
from langchain_ollama import ChatOllama
from models import SupervisorDecision
from llm import eval_llm
from memory.working_memory import memory
from tracing.helpers import trace_node



supervisor_model = eval_llm.with_structured_output(SupervisorDecision, method="json_schema", include_raw=True)
def supervisor_node(state: AgentState):
    """"Create a plan and choose the appropraite specialist tasks"""
    prompt = f"""
                You are the supervisior of a multi-agent system.

                User task:
                {state['task']}

                Relevant memories from previous tasks:
                {state.get("relevant_memories", [])}

                Human review feedback:
                {state.get("human_feedback", "None")}

                If a human rejected or modified a previous approach,
                use their feedback when creating the new plan.
                Do not repeat the rejected approach without justification.

                Break the request into an ordered execution plan.

                Available specialists:
                - research: gathers and explains factual information
                - writing: drafts, rewrites, summarizes, and organizes content

                For every subtask provide:

                - a unique ID such as task_1
                - a clear description
                - the specialist responsible
                - required inputs
                - dependencies
                - expected output format
                - estimated complexity
                Do not create multiple back to back subtask with the same specialist.
                Just have one subtask for the one specialist to complete the work
                Dependency rules:
                - dependencies must reference subtask IDs.
                - only depend on tasks appearing earlier in the plan.
                - use [] when no dependencies exist.
                - do not create unnecessary subtasks.
                - make sure completing all subtasks completes the user's request.
    """
    with trace_node(
        "agent.supervisor",
        state,
        agent_type="supervisor",
        prompt = prompt
    ) as (span, trace):
        decision = supervisor_model.invoke(
            prompt
        )

        raw = decision["raw"]
        decision = decision["parsed"]
        usage = raw.usage_metadata
        trace["response"] = str(decision)

        trace["decision"] = (
            f"Created {len(decision.subtasks)} subtasks"
        )
        span.set_attribute(
            "supervisor.confidence",
            decision.confidence
        )

        span.set_attribute(
            "supervisor.subtask_count",
            len(decision.subtasks)
        )

        span.set_attribute(
        "llm.input_tokens",
            usage.get("input_tokens", 0)
        )

        span.set_attribute(
            "llm.output_tokens",
            usage.get("output_tokens", 0)
        )

        subtasks = [
            subtask.model_dump()
            for subtask in decision.subtasks
        ]
        memory.save(
            state["task_id"],
            "plan",
            subtasks,
        )
        return {
            "subtasks": subtasks,
            "supervisor_confidence": decision.confidence,
            "approval_id": None,
            "approval_status": None,
            "needs_human": False,
        }
