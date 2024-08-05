from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.propagate import extract, inject
import ray
from ray_integration import call_ray_task
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a FastAPI app
app = FastAPI()

# Set up tracing with a specific service name
resource = Resource(attributes={ResourceAttributes.SERVICE_NAME: "fastapi-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument FastAPI and Requests (for external HTTP calls)
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Initialize Ray with the dashboard enabled
ray.init(include_dashboard=True, dashboard_host="0.0.0.0")


@app.get("/")
async def read_root(request: Request):
    tracer = trace.get_tracer(__name__)

    # Extract the request ID from headers or generate a new one
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info(f"Handling request with request ID: {request_id}")

    # Extract the context from the incoming request
    context = extract(request.headers)
    token = attach(context)

    # Start a new span and add request ID as an attribute
    with tracer.start_as_current_span("fastapi-request-span") as span:
        span.set_attribute("request.id", request_id)

        # Inject the current context into the headers
        headers = {}
        inject
        (headers, context)
        logger.info(f"Context injected into headers: {headers}")

        # Call the Ray task and pass the current trace context and request ID
        result = await call_ray_task(request_id, headers)

        detach(token)
        return {"message": "Hello World", "result": result, "request_id": request_id}


@app.get("/throw-error")
async def throw_error():
    raise ValueError("An error occurred")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
