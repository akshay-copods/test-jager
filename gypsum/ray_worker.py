import ray
import argparse
from opentelemetry import trace


# Define the Actor class
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        print(f"Counter incremented: {self.value}")
        return self.value

    def get_value(self):
        print(f"Counter incremented: {self.value}")
        return self.value

def main(id, action):
    # Initialize Ray
    ray.init(_tracing_startup_hook="gypsum.ray_tracer:setup_tracing")

    # Create the actor
    counter = Counter.remote()
    tracer = trace.get_tracer(__name__)
    if action == "increment":
        with tracer.start_as_current_span(
            "ray-increment-operation",
            attributes={"gypsum.key1": "parent1"} # Add submission ID here
        ):
            result = ray.get(counter.increment.remote())
    elif action == "value":
        with tracer.start_as_current_span(
            "ray-getvalue-operation",
            attributes={"gypsum.key1": "parent1"} # Add submision ID here
        ):
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
