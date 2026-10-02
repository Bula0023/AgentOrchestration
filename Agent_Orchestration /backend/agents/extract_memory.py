from llm import llm
from models import MemoryExtraction
from state import AgentState
from memory.semantic_memory import semantic_memory
memory_extraction_model = llm.with_structured_output(
    MemoryExtraction
)

def extract_memory_node(state: AgentState):

    extraction = memory_extraction_model.invoke(
        f"""
        Extract useful long-term memory from this completed task.

        Original user request:
        {state["task"]}

        Execution plan:
        {state["subtasks"]}

        Completed subtask results:
        {state["subtask_results"]}

        Final answer:
        {state["final_answer"]}

        Extract:
        - what the user requested
        - the approach that successfully completed the task
        - tools that were actually used
        - useful domain-specific facts discovered
        - user preferences that were actually demonstrated

        Do not invent information.
        Only extract information supported by this task.
        """
    )

    memory_text = f"""
    User requet:
    {extraction.user_request}

    Successful apporaches:
    {", ".join(extraction.successful_approaches)}

    Tools used:
    {", ".join(extraction.tools_used)}

    Domain facts:
    {"; ".join(extraction.domain_facts)}

    User preferences:
    {"; ".join(extraction.user_preferences)}
    """

    semantic_memory.add_memory(
        memory_text,
        state["user_id"],
        state["task_id"]
    )

    return {}