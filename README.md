WELCOME TO OUR FIRST DEEP LEARNING PROJECT ヾ(＠⌒ー⌒＠)ノ

# ACOS-DL-Cloud

ACOS-DL-Cloud is an automatic supermarket checkout system that combines a YOLO-based computer vision pipeline, a FastAPI backend, and a React dashboard. The application tracks items from video, builds receipt data, and lets users review and confirm checkout sessions.

Authors:

- Mayara Labidi
- Roua Khribiche

## Overview

The project is organized around three layers:

- `pipeline/` implements the detection, tracking, clustering, and pricing logic.
- `api/` exposes the FastAPI service for sessions, products, health checks, and confirmation workflows.
- `frontend/` provides the cashier-style interface for uploads, review, and history.

The repository also includes Alembic migrations, Dockerfiles, Kubernetes manifests, and a GitHub Actions workflow for build and deployment.

## Key Features

- Video-based product detection and receipt generation.
- Session review with overrides and confirmation.
- FastAPI backend with CORS, database initialization, and health endpoints.
- React + Vite frontend for a responsive operator dashboard.
- Docker, Kubernetes, and CI/CD support for local and cloud deployment.

## Quick Start

The fastest way to run the project locally is with Docker Compose.

1. Install Docker Desktop and make sure Docker Compose is available.
2. Create your environment file:

```powershell
Copy-Item .env.example .env
```

3. Update `.env` with at least `DATABASE_URL`. If you are running locally with Compose, you can use a PostgreSQL connection string that matches the bundled database service.
4. Start the application:

```powershell
docker compose up --build
```

5. Open the frontend at http://localhost:3000.
6. Check the API health endpoint at http://localhost:8080/health.

## Local Development

If you prefer running services separately:

### Backend

1. Use Python 3.12.
2. Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Start the API:

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend

1. Install dependencies:

```powershell
cd frontend
npm install
```

2. Start the development server:

```powershell
npm run dev
```

By default the Vite app runs on http://localhost:5173.

## Environment Variables

The backend reads settings from the environment or a local `.env` file. The most important value is `DATABASE_URL`.

Common settings include:

- `DATABASE_URL` - required PostgreSQL connection string.
- `APP_ENV` - runtime mode such as `dev`, `test`, or `prod`.
- `LOG_LEVEL` - log verbosity.
- `CORS_ORIGINS` - comma-separated frontend origins allowed to call the API.
- `GCP_PROJECT_ID`, `GCS_BUCKET_NAME`, `GCS_MODEL_PATH`, `GCS_VIDEO_BUCKET` - optional cloud storage and model settings.

## Deployment

The Kubernetes manifests under `k8s/` support environment-specific deployment overlays for `dev`, `test`, and `prod`. The GitHub Actions workflow builds the backend and frontend images, then deploys to the matching namespace when code is pushed to the corresponding branch:

- `dev` branch deploys to the dev namespace.
- `staging` branch deploys to the test namespace.
- `main` branch deploys to production.

In production, the frontend service is exposed through a Kubernetes `LoadBalancer`. After deployment, find the external IP with:

```powershell
kubectl get svc frontend-service -n prod
```

Share the external IP with your classmates so they can open the dashboard in a browser. The API service is also exposed in prod and is typically used by the frontend rather than accessed directly.

## Secrets

Do not commit real credentials or database URLs to GitHub. Inject secrets at deploy time instead of storing them in Kubernetes YAML.

Example commands:

```powershell
# Dev namespace: create the in-cluster Postgres credentials before applying the overlay
kubectl create secret generic checkout-secrets -n dev `
	--from-literal=POSTGRES_USER=checkout `
	--from-literal=POSTGRES_PASSWORD=<dev-password> `
	--from-literal=POSTGRES_DB=checkout `
	--from-literal=DATABASE_URL=postgresql+asyncpg://checkout:<dev-password>@checkout-postgres.dev.svc.cluster.local:5432/checkout

# Test namespace: point to the test database endpoint
kubectl create secret generic checkout-secrets -n test `
	--from-literal=DATABASE_URL=<test-database-url>

# Prod namespace: point to the production database endpoint
kubectl create secret generic checkout-secrets -n prod `
	--from-literal=DATABASE_URL=<prod-database-url>
```

If you use Secret Manager or External Secrets, keep the repository free of live values and sync them into the cluster during deploy.

## Validation

Run the test suite with:

```powershell
python -m pytest tests -q
```

The current workspace passes this test command.
