from fastapi import FastAPI
from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider, Counter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Initialize FastAPI
app = FastAPI()

# Service name is required for most backends
resource = Resource(attributes={SERVICE_NAME: "your-service-name"})

# Start Prometheus client
start_http_server(port=9464, addr="localhost")

# Initialize PrometheusMetricReader which pulls metrics from the SDK
reader = PrometheusMetricReader()
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create a meter and two counters: one for HTTP requests and one for sheep
meter = metrics.get_meter("your-meter-name")
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1",
)
sheep_counter = meter.create_counter(
    name="sheep_counter_total",
    description="Total number of sheep incremented",
    unit="1",
)


# Define a simple route
@app.get("/")
async def read_root():
    # Increment the counter for the root endpoint
    request_counter.add(1, {"endpoint": "/"})
    return {"Hello": "World"}


# Define a route to increment the sheep counter
@app.post("/increment")
async def increment_sheep():
    # Increment the sheep counter
    sheep_counter.add(1)
    return {"message": "Sheep counter incremented!"}


# Define another route to demonstrate metrics
@app.get("/custom-metrics")
async def get_metrics():
    # Increment the counter for the custom metrics endpoint
    request_counter.add(1, {"endpoint": "/custom-metrics"})
    return {"message": "Metrics are being collected!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
