import time

from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import (
    Status,
    StatusCode,
)

from tracing.telemetry import tracer
from tracing.trace_store import trace_store


@contextmanager
def trace_node(
    name: str,
    state: dict,
    agent_type: str | None = None,
    prompt: str | None = None,
):

    task_id = state["task_id"]

    start = time.perf_counter()

    parent_span = trace.get_current_span()

    parent_context = (
        parent_span.get_span_context()
    )

    parent_span_id = None

    if parent_context.is_valid:

        parent_span_id = (
            f"0x{parent_context.span_id:016x}"
        )


    with tracer.start_as_current_span(
        name
    ) as span:

        context = span.get_span_context()

        otel_trace_id = (
            f"0x{context.trace_id:032x}"
        )

        otel_span_id = (
            f"0x{context.span_id:016x}"
        )


        node = {
            "id": otel_span_id,

            "task_id": task_id,

            "trace_id": otel_trace_id,

            "span_id": otel_span_id,

            "parent_span_id":parent_span_id,

            "name":name,

            "agent":agent_type,

            "status":"success",

            "summary": None,

            "tools":[],

            "latency_ms":None,

            "input_tokens": span.attributes.get("llm.input_tokens",0),
            "output_tokens": span.attributes.get("llm.output_tokens", 0),
            "total_tokens": span.attributes.get("llm.input_tokens", 0) + span.attributes.get("llm.output_tokens", 0),


            "cost":None,

            "error": None,

            "prompt": prompt,

            "response": None,
        }


        span.set_attribute(
            "task.id",
            task_id
        )

        if agent_type:

            span.set_attribute(
                "agent.type",
                agent_type
            )


        try:

            yield span, node

            span.set_attribute(
                "trace.status",
                node["status"]
            )

            span.set_status(
                Status(
                    StatusCode.OK
                )
            )


        except Exception as error:

            node["status"] = (
                "failure"
            )

            node["error"] = str(
                error
            )

            span.set_attribute(
                "trace.status",
                "failure"
            )

            span.record_exception(
                error
            )

            span.set_status(
                Status(
                    StatusCode.ERROR,
                    str(error)
                )
            )

            raise


        finally:

            latency_ms = (
                time.perf_counter()
                - start
            ) * 1000

            node["latency_ms"] = (
                latency_ms
            )

            span.set_attribute(
                "latency_ms",
                latency_ms
            )

            trace_store.add_node(
                task_id,
                node
            )

            print(
                "NODE STORED:",
                node
            )