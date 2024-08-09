from fastapi import FastAPI
import uvicorn
from ray.job_submission import JobSubmissionClient
import time

# Initialize FastAPI
app = FastAPI()

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
    # Submit the Ray job for incrementing the counter
    submission_id = submit_ray_job("increment")

    # Return immediately without waiting for the job to finish
    return {"message": f"Job {submission_id} for incrementing counter started"}


@app.get("/value")
async def get_counter_value():
    # Submit the Ray job for getting the counter value
    submission_id = submit_ray_job("value")

    # Return immediately without waiting for the job to finish
    return {"message": f"Job {submission_id} for getting counter value started"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
