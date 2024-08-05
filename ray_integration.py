import ray
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.propagate import extract
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up tracing with a specific service name for Ray
resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: "ray-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


@ray.remote
def ray_task(headers, request_id):
    tracer = trace.get_tracer(__name__)

    # Extract the context in the Ray task
    context = extract(headers)
    token = attach(context)
    with tracer.start_as_current_span("ray-task-span") as span:
        span.set_attribute("request.id", request_id)
        # Your Ray task logic here
        result = "Ray task result"
        logger.info(f"Ray task completed with result: {result}")
    detach(token)
    return result


async def call_ray_task(request_id, headers):
    # Call the Ray task, passing the context and request ID
    result_ref = ray_task.remote(headers, request_id)

    # Use ray.get to fetch the result
    result = ray.get(result_ref)
    return result
