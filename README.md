# ACOS-DL-Cloud

Automatic supermarket checkout system built with a YOLOv11m pipeline, FastAPI backend, and React dashboard.

## What’s included

- Python ML pipeline for cross-class NMS and spatial cluster tracking
- FastAPI backend for session processing, overrides, and confirmation
- React + Vite frontend for video upload, receipt review, and history
- Alembic migrations, Dockerfiles, Kubernetes manifests, and GitHub Actions CI/CD

## Quick start

1. Use Python 3.12 for this project. On Windows, create the venv with `py -3.12 -m venv .venv`.
2. Activate it with `.venv\Scripts\Activate.ps1` and make sure `pip --version` points to `.venv`.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set `DATABASE_URL` and any GCP values you need.
5. Run the test suite with `python -m pytest tests -q`.

If you already created `.venv` with Python 3.13, delete it and recreate it with Python 3.12. NumPy and the rest of the stack are pinned for the supported 3.12 environment.

## Project layout

- `pipeline/` contains the detection pipeline and pricing table.
- `api/` contains the FastAPI app, ORM models, schemas, and services.
- `frontend/` contains the cashier dashboard.
- `migrations/` contains the Alembic migration bootstrap.
- `k8s/` contains environment-specific deployment manifests.

## Validation

The current workspace passes `pytest tests -q`.

## Secrets

Do not commit real credentials or database URLs to GitHub.

The application reads `DATABASE_URL` from the environment, so inject secrets at deploy time instead of storing them in Kubernetes YAML.

Examples:

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

If you use Secret Manager or External Secrets, keep the repo free of the real values and sync them into the cluster during deploy.
