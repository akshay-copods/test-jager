from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

tracer_provider = None


def get_tracer():
    global tracer_provider
    if tracer_provider is None:
        init_tracer()
    return trace.get_tracer(__name__)


def init_tracer():
    global tracer_provider
    tracer_provider = TracerProvider(
        resource=Resource.create({"service.name": "fastapi-ray-service"})
    )

    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)
