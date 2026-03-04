# Deploy FastAPI User Login to Google Cloud Run

Step-by-step guide to deploy this app to **Google Cloud Run** using your existing Dockerfile.

## Prerequisites

1. **Google Cloud account** with billing enabled.
2. **gcloud CLI** installed and logged in:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Production secrets**: For production you need:
   - A strong `SECRET_KEY` (e.g. `openssl rand -hex 32`).
   - A **PostgreSQL** database (Cloud SQL or external). Format:  
     `postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE`

---

## 1. Enable required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## 2. Create an Artifact Registry repository (one-time)

```bash
# Replace REGION (e.g. us-central1) and REPO_NAME (e.g. fastapi-apps)
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --description="Docker images for FastAPI apps"
```

If you prefer to use the default **Container Registry** (deprecated but still works):

```bash
gcloud services enable containerregistry.googleapis.com
# Image will be: gcr.io/PROJECT_ID/IMAGE_NAME
```

---

## 3. Build and push the image

From the **project root** (where `Dockerfile` lives):

**Option A – Artifact Registry (recommended)**

```bash
# Set these once
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export REPO_NAME=fastapi-apps
export IMAGE_NAME=fastapi-user-login

# Build and push in one step (Cloud Build runs in GCP)
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest
```

**Option B – Container Registry (gcr.io)**

```bash
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/fastapi-user-login:latest
```

---

## 4. Deploy to Cloud Run

**Minimal deploy (env vars on command line):**

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export REPO_NAME=fastapi-apps
export IMAGE_NAME=fastapi-user-login

gcloud run deploy fastapi-user-login \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars "SECRET_KEY=YOUR_MIN_32_CHAR_SECRET_KEY" \
  --set-env-vars "DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname" \
  --set-env-vars "ENVIRONMENT=production"
```

**Using a `.env` file (do not commit it):**

Create a file e.g. `cloudrun.env` with:

```
SECRET_KEY=your-production-secret-key-min-32-chars
DATABASE_URL=postgresql+asyncpg://user:pass@/cloudsql/PROJECT:REGION:INSTANCE/dbname
ENVIRONMENT=production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Then:

```bash
gcloud run deploy fastapi-user-login \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --env-vars-file cloudrun.env
```

**Optional:** Use **Secret Manager** for `SECRET_KEY` and `DATABASE_URL` instead of plain env vars (see [GCP Secret Manager](https://cloud.google.com/secret-manager/docs)).

---

## 5. One-command deploy from source (no separate build step)

Cloud Run can build from source and deploy in one step:

```bash
gcloud run deploy fastapi-user-login \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SECRET_KEY=YOUR_SECRET,DATABASE_URL=postgresql+asyncpg://...,ENVIRONMENT=production"
```

This uses your `Dockerfile` in the current directory. Replace env values with your real secrets.

---

## 6. After deploy

- The command prints the **service URL**, e.g.  
  `https://fastapi-user-login-xxxxx-uc.a.run.app`
- **API docs:** `https://YOUR_SERVICE_URL/docs`
- **Health check:** `https://YOUR_SERVICE_URL/health`

---

## 7. Database for production

- **Cloud SQL (PostgreSQL):** Create an instance, then use the connection name for the socket or the instance’s public IP in `DATABASE_URL`.
- **With Cloud Run + Cloud SQL:** Use the Cloud SQL Auth Proxy sidecar or connect via private IP/VPC and set `DATABASE_URL` to the instance.

Example `DATABASE_URL` for Cloud SQL (public IP):

```
postgresql+asyncpg://user:password@10.x.x.x:5432/dbname
```

---

## 8. Summary of env vars for Cloud Run

| Variable | Required | Example |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Long random string (min 32 chars) |
| `DATABASE_URL` | Yes (prod) | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `ENVIRONMENT` | Recommended | `production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` |
| `PORT` | No | Set by Cloud Run (8080) |

Your Dockerfile already uses `PORT` and binds to `0.0.0.0`, so no code changes are needed for Cloud Run.

---

## Deploy on merge from Git (CI/CD)

To **integrate with Git and deploy automatically when you merge to `main`**, see **[GIT-AND-CICD.md](GIT-AND-CICD.md)**. It covers:

- Initializing the repo and pushing to GitHub (or Cloud Source Repositories).
- **Cloud Build trigger**: connect the repo, run `cloudbuild-deploy.yaml` on every push to `main` (build → push image → deploy to Cloud Run).
- **GitHub Actions**: optional workflow in `.github/workflows/deploy-cloudrun.yml` that builds, pushes, and deploys on push to `main`.
