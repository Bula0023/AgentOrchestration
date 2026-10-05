from typing import Literal, Callable, Type
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Callable, Literal, Type
from datetime import datetime
from collections import defaultdict, deque
import subprocess
import time
from tracing.telemetry import tracer

from .code_execution import execute_code
from .schemas import (
    FileReadInput,
    FileReadOutput,
    WebSearchInput,
    WebSearchOutput,
    DatabaseQueryInput,
    DatabaseQueryOutput,
    APICallInput,
    APICallOutput,
    CodeExecutionInput, 
    CodeExecutionOutput,
    FileWriteInput,
    FileWriteOutput
)

from .implement_tool import (
    read_file,
    write_file
)
from .web_search import web_search

from .database import query_database

from .api import call_api

SpecialistName = Literal["research","writing", "code", "data"]

class ToolInvocationLog(BaseModel):
    timestamp: datetime
    task_id: str
    tool_name: str
    specialist: str

    inputs: dict
    outputs: dict | None = None

    latency_ms: float

    success: bool
    error: str | None = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    allowed_specialists: list[SpecialistName]

    rate_limit: int = Field(
        description="Max calls per minute"
    )
    function: Callable

class ToolRegistry:

    def __init__(self):
        self.tools: dict[str, ToolDefinition] = {}
        self.logs: list[ToolInvocationLog] = []
        self.call_history = defaultdict(deque)

    def register(self, tool: ToolDefinition):
        if tool.name in self.tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )
        self.tools[tool.name] = tool

    def get(self, name:str) -> ToolDefinition:
        if name not in self.tools:
            raise ValueError(
                f"Unknown tool: {name}"
            )
        return self.tools[name]
    
    def tools_for_specialist(self, specialist: SpecialistName) -> list[ToolDefinition]:
        return [tool for tool in self.tools.values() if specialist in tool.allowed_specialists]
    
    def check_rate_limit(self, tool):
        now = time.time()
        history = self.call_history[tool.name]

        while history and now - history[0] > 60:
            history.popleft()

        if len(history) >= tool.rate_limit:
            raise RuntimeError(
                f"Rate limit exceeded for {tool.name}"
            )
        # Record this call
        history.append(now)

    def get_logs_for_task(self, task_id: str):
        return [log for log in self.logs if log.task_id == task_id]

    def invoke_tool(self,task_id:str, tool_name: str, specialist: SpecialistName, inputs: dict):
        with tracer.start_as_current_span(
                f"tool.{tool_name}"
            ) as span:

            span.set_attribute(
                "tool.name",
                tool_name
            )

            span.set_attribute(
                "tool.specialist",
                specialist
            )
            start = time.perf_counter()


            try:
                #1. find the tool
                tool = self.get(tool_name)
                print("tool_name", tool)

                #permission
                if specialist not in tool.allowed_specialists:
                    raise PermissionError(
                        f"{specialist} cannot use {tool_name}"
                    )
                # check rate limit
                self.check_rate_limit(tool)
                #validate input
                validated_inputs = tool.input_schema.model_validate(inputs)
                # Run the real tool function
                result = tool.function(validated_inputs)
                # Validate output
                validated_output = tool.output_schema.model_validate(result)
                #latency
                latency = (
                    time.perf_counter() - start
                ) * 1000

                #log success calls
                self.logs.append(
                    ToolInvocationLog(
                        timestamp=datetime.now(),
                        task_id=task_id,
                        tool_name=tool_name,
                        specialist=specialist,
                        inputs=inputs,
                        outputs=validated_output.model_dump(),
                        latency_ms=latency,
                        success=True
                    )
                )
                span.set_attribute(
                    "tool.success",
                    True
                )
                span.set_attribute("tool.latency_ms", latency)
                return validated_output
            except Exception as e:
                latency = (time.perf_counter() - start).seconds * 1000
                self.logs.append(
                    ToolInvocationLog(
                        timestamp=time.perf_counter(),
                        task_id=task_id,
                        tool_name=tool_name,
                        specialist=specialist,
                        inputs=inputs,
                        outputs=None,
                        latency_ms=latency,
                        success=False,
                        error=str(e)
                    )
                )
                span.set_attribute("tool.success", False)
                span.set_attribute("tool.latency_ms", latency)
                span.set_attribute("error.message", str(e))

                span.record_exception(e)
                raise



registry = ToolRegistry()
read_file_tool = ToolDefinition(
        name="file_read",
        description="Read the contents of a file",
        input_schema=FileReadInput,
        output_schema=FileReadOutput,
        allowed_specialists=["research", "writing"],
        rate_limit=30,
        function=read_file
    )

registry.register(read_file_tool)

web_search_tool = ToolDefinition(
    name="web_search",
    description="Search the web for information",
    input_schema=WebSearchInput,
    output_schema=WebSearchOutput,
    allowed_specialists=["research"],
    rate_limit=60,
    function=web_search
)
registry.register(web_search_tool)

file_write_tool = ToolDefinition(
    name="file_write",
    description="Write content to a file",
    input_schema=FileWriteInput,
    output_schema=FileWriteOutput,
    allowed_specialists=["writing"],
    rate_limit=30,
    function=write_file
)
registry.register(file_write_tool)

code_execution_tool = ToolDefinition(
    name="code_execution",
    description="Execute code in a sandboxed environment",
    input_schema=CodeExecutionInput,
    output_schema=CodeExecutionOutput,
    allowed_specialists=["code"],
    rate_limit=10,
    function=execute_code
)
registry.register(code_execution_tool)

database_query_tool = ToolDefinition(
    name="database_query",
    description="Query the database",
    input_schema=DatabaseQueryInput,
    output_schema=DatabaseQueryOutput,
    allowed_specialists=["data"],
    rate_limit=20,
    function=query_database
)
registry.register(database_query_tool)

api_call_tool = ToolDefinition(
    name="api_call",
    description="Make an Api call to an external service",
    input_schema=APICallInput,
    output_schema=APICallOutput,
    allowed_specialists=["research","data"],
    rate_limit=50,
    function=call_api
)

registry.register(api_call_tool)


