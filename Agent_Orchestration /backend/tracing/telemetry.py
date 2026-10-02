from opentelemetry import trace

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


resource = Resource.create({
    "service.name": "agent-orchestration"
})


provider = TracerProvider(
    resource=resource
)


provider.add_span_processor(
    BatchSpanProcessor(
        ConsoleSpanExporter()
    )
)


trace.set_tracer_provider(provider)


tracer = trace.get_tracer(
    "agent-orchestration"
)