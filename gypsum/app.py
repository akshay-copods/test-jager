from fastapi import FastAPI, HTTPException
import uvicorn
from ray.job_submission import JobSubmissionClient
import time
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize FastAPI
app = FastAPI()

# Initialize Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set up the tracer provider with a specific service name for FastAPI
resource = Resource.create({"service.name": "fastapi-service-new"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app)

# Initialize the JobSubmissionClient with the address of your Ray cluster
client = JobSubmissionClient(
    "http://127.0.0.1:8265"
)  # Replace with your Ray cluster address


def submit_ray_job(action: str):
    job_id = f"ray-job-{time.time()}"  # Unique job ID
    job_cmd = f"python gypsum/ray_worker.py --id {job_id} --action {action}"
    submission_id = client.submit_job(
        entrypoint=job_cmd,
        runtime_env={
            "working_dir": "./"
        }
    )
    return submission_id


@app.post("/increment")
async def increment_counter():
    # IMPORTANT: try-except is needed for opentelemetry to record the errors.
    try:
        submission_id = submit_ray_job("increment")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")
    return {"message": f"Job {submission_id} for incrementing counter started"}


@app.get("/value")
async def get_counter_value():
    # IMPORTANT: try-except is needed for opentelemetry to record the errors.
    try:
        submission_id = submit_ray_job("value")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")
    return {"message": f"Job {submission_id} for getting counter value started"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
