import ray
import argparse
import time
from opentelemetry import trace


# Define the Actor class
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        time.sleep(7)  # Simulate a delay
        self.value += 1
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(f"ray-increment-operation"):
            print(f"Counter incremented: {self.value}")
        return self.value

    def get_value(self):
        time.sleep(7)  # Simulate a delay
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(f"ray-get-operation"):
            print(f"Counter incremented: {self.value}")
        return self.value


def main(id, action):
    # Initialize Ray
    ray.init(_tracing_startup_hook="gypsum.ray_tracer:setup_tracing")

    # Create the actor
    counter = Counter.remote()
    if action == "increment":
        result = ray.get(counter.increment.remote())
    elif action == "value":
        result = ray.get(counter.get_value.remote())

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
