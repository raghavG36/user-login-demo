# Git integration and deploy on merge to Cloud Run

This guide covers:

1. **Initialize Git** and connect the repo to GitHub (or GitLab / Cloud Source Repositories).
2. **Deploy automatically on merge** using either **Cloud Build triggers** (GCP-native) or **GitHub Actions**.

Prerequisites: you’ve already done a **one-time manual deploy** to Cloud Run and set env vars (`SECRET_KEY`, `DATABASE_URL`, `ENVIRONMENT`) on the service. The pipeline will only **build and deploy the new image**; it won’t change those env vars.

---

## 1. Initialize Git and push to a remote

From the project root:

```bash
# Initialize repo (if not already)
git init

# Add files ( .gitignore already excludes .env, .venv, app.db, etc.)
git add .
git commit -m "Initial commit: FastAPI user login + Cloud Run deploy"

# Add remote (replace with your repo URL)
# GitHub:
git remote add origin https://github.com/YOUR_ORG/fastapi-user-login.git
# or SSH:
# git remote add origin git@github.com:YOUR_ORG/fastapi-user-login.git

# Push (use main or your default branch)
git branch -M main
git push -u origin main
```

Use a **branch strategy** (e.g. `main` = production, `develop` = staging). The “deploy on merge” trigger will run when you push/merge to the branch you choose (e.g. `main`).

---

## 2. Deploy on merge with Cloud Build (recommended)

Cloud Build can watch your Git repo and run **build + deploy** on every push (or merge) to a branch.

### 2.1 Connect your repo to Cloud Build

**Option A – GitHub**

1. In [Google Cloud Console](https://console.cloud.google.com/) → **Cloud Build** → **Triggers**.
2. **Connect repository** → choose **GitHub** → authenticate and select the repo (e.g. `fastapi-user-login`).
3. If you use a **GitHub App** (recommended): install it for the org/repo when prompted.

**Option B – Cloud Source Repositories (mirror)**

1. In **Cloud Build** → **Triggers** → **Connect repository** → **Cloud Source Repositories**.
2. Create a new repo or link an existing one.
3. Add a **push mirror** from GitHub to Cloud Source Repositories (in GitHub repo **Settings** → **Mirrors**), or push directly to the CSR repo.

### 2.2 Grant the Cloud Build service account permission to deploy Cloud Run

Cloud Build runs as a service account. It needs permission to deploy to Cloud Run and push to Artifact Registry:

```bash
# Get your project number and the default Cloud Build SA
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Run Admin and Service Account User to Cloud Build
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Artifact Registry write (if using Artifact Registry)
gcloud artifacts repositories add-iam-policy-binding fastapi-apps \
  --location=us-central1 \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

Adjust `fastapi-apps` and `us-central1` if you use different repo name or region.

### 2.3 Create the trigger

1. **Cloud Build** → **Triggers** → **Create trigger**.
2. **Name:** e.g. `deploy-fastapi-user-login`.
3. **Event:** Push to a branch.
4. **Source:** the connected repo; **Branch:** `^main$` (regex; use the branch you deploy from).
5. **Configuration:** **Cloud Build configuration file (yaml or json)**.
6. **Location:** Repository; **Cloud Build configuration file path:** `cloudbuild-deploy.yaml`.
7. **Substitution variables** (optional):  
   `_REGION` = `us-central1`, `_REPO_NAME` = `fastapi-apps`, `_IMAGE_NAME` = `fastapi-user-login`, `_SERVICE_NAME` = `fastapi-user-login`.
8. Save.

From now on, every **push (or merge) to `main`** will run `cloudbuild-deploy.yaml`: build image → push to Artifact Registry → deploy to Cloud Run.

### 2.4 First-time setup: Artifact Registry repo

If you haven’t created the Artifact Registry repo yet:

```bash
gcloud artifacts repositories create fastapi-apps \
  --repository-format=docker \
  --location=us-central1
```

---

## 3. Deploy on merge with GitHub Actions (alternative)

A workflow is included: **`.github/workflows/deploy-cloudrun.yml`**. It runs on every push to `main` (and can be triggered manually). It builds the Docker image, pushes to Artifact Registry, and deploys to Cloud Run.

### 3.1 Create a GCP service account for GitHub Actions

```bash
PROJECT_ID=your-gcp-project-id
SA_NAME=github-actions-cloudrun
SA_EMAIL=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud iam service-accounts create $SA_NAME --display-name="GitHub Actions Cloud Run deploy"

# Permissions: push images, deploy Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/iam.serviceAccountUser"

# Create key and download JSON (keep it secret)
gcloud iam service-accounts keys create key.json --iam-account=$SA_EMAIL
# Copy key.json contents into GitHub secret GCP_SA_KEY; then delete key.json
```

### 3.2 GitHub repository secrets

In the repo: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret            | Description |
|-------------------|-------------|
| `GCP_PROJECT_ID`  | Your GCP project ID. |
| `GCP_SA_KEY`      | Full contents of the service account JSON key file. |

After that, every **push (or merge) to `main`** will build and deploy to Cloud Run. For production, consider **Workload Identity Federation** so you don’t store a key in GitHub.

---

## 4. Summary

| Step | Action |
|------|--------|
| 1 | `git init`, add remote, push to `main` (or your deploy branch). |
| 2 | Connect the repo to Cloud Build (GitHub or Cloud Source Repositories). |
| 3 | Grant Cloud Build SA: Cloud Run Admin, Service Account User, Artifact Registry Writer. |
| 4 | Create trigger: push to `main` → config file `cloudbuild-deploy.yaml`. |
| 5 | Merge (or push) to `main` → build and deploy run automatically. |

Env vars (`SECRET_KEY`, `DATABASE_URL`, etc.) are **not** in the pipeline; they stay on the Cloud Run service (set once manually or via Secret Manager). The CI only updates the **container image** and redeploys.
