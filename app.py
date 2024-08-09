from fastapi import FastAPI
import uvicorn
from ray.job_submission import JobSubmissionClient
import time
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize FastAPI
app = FastAPI()

# Initialize Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set up the tracer provider and span processor
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)

# Initialize the JobSubmissionClient with the address of your Ray cluster
client = JobSubmissionClient(
    "http://127.0.0.1:8265"
)  # Replace with your Ray cluster address


def submit_ray_job(action: str):
    job_id = f"ray-job-{time.time()}"  # Unique job ID
    job_cmd = f"python ray_worker.py --id {job_id} --action {action}"
    submission_id = client.submit_job(entrypoint=job_cmd)
    return submission_id


@app.post("/increment")
async def increment_counter():
    submission_id = submit_ray_job("increment")
    return {"message": f"Job {submission_id} for incrementing counter started"}


@app.get("/value")
async def get_counter_value():
    submission_id = submit_ray_job("value")
    return {"message": f"Job {submission_id} for getting counter value started"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
