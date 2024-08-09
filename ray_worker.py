import ray
import argparse
import time
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set up the tracer provider with a specific service name for Ray
resource = Resource.create({"service.name": "ray-worker-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))


# Define the Actor class
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        time.sleep(7)  # Simulate a delay
        self.value += 1
        return self.value

    def get_value(self):
        time.sleep(7)  # Simulate a delay
        return self.value


def main(id, action):
    # Initialize Ray
    ray.init()

    # Create the actor
    counter = Counter.remote()

    # Perform the action based on the command-line argument
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(f"ray-{action}-operation"):
        if action == "increment":
            result = ray.get(counter.increment.remote())
            print(f"Counter incremented: {result}")
        elif action == "value":
            result = ray.get(counter.get_value.remote())
            print(f"Counter value: {result}")

    # Shutdown Ray
    ray.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ray Actor Operations")
    parser.add_argument("--id", type=str, required=True, help="ID for the operation")
    parser.add_argument(
        "--action",
        type=str,
        choices=["increment", "value"],
        required=True,
        help="Action to perform",
    )

    args = parser.parse_args()

    main(args.id, args.action)
