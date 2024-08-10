# Jaegar tracing setup

Follow these instructions to setup tracing.

# Install modules

`pip install -e .`

# Start Ray

`ray start --head --tracing-startup-hook=gypsum.ray_tracer:setup_tracing`

# Start API server

`python gypsum/app.py`

# Execute a FastAPI request

You can use the dashboard (http://localhost:8000/docs) to do this

# View traces on Jaegar dashboard

The dashboard is available at http://localhost:16686

You can filter by service names: ray-worker-service-new, fastapi-service-new
