import ray
import argparse
import time  # Import time module for adding delay


# Define the Actor class
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        time.sleep(7)  # Add a 7-second delay before incrementing the counter
        self.value += 1
        return self.value

    def get_value(self):
        time.sleep(7)  # Add a 7-second delay before returning the value
        return self.value


def main(id, action):
    # Initialize Ray
    ray.init()

    # Create the actor
    counter = Counter.remote()

    # Perform the action based on the command-line argument
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
