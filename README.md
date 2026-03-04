# FastAPI User Login & Calculator

Production-ready FastAPI application with JWT authentication and a protected calculator module. Uses async SQLAlchemy (SQLite for local dev, PostgreSQL-ready), Pydantic validation, and Docker/Cloud Run–friendly setup.

## Features

- **Auth**: User registration, login (OAuth2 password flow), JWT access tokens, protected `/auth/me`
- **Calculator**: Protected endpoints for add, subtract, multiply, divide (JSON in/out, divide-by-zero handled)
- **Stack**: FastAPI, Uvicorn, Gunicorn, SQLAlchemy (async), Pydantic, passlib (bcrypt), python-jose (JWT)
- **Database**: Auto-create tables on startup; SQLite locally, configurable for PostgreSQL
- **React frontend**: Register, login, calculator, and Actions Performed screen (session history)

## Project structure

```
/app                 → FastAPI backend
  /api/auth          → router, schemas, service
  /api/calculator    → router, schemas, service
  /core              → config, security
  /db                → base, session, models
  main.py
/frontend            → React (Vite) UI
  src/pages          → Register, Login, Calculator, ActionsPerformed
  src/context        → AuthContext, ActionsContext
  src/api            → API client
Dockerfile, docker-compose.yml, .env.example, requirements.txt
```

## Local run

1. **Create virtualenv and install deps**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Environment**

   Copy `.env.example` to `.env` and set at least `SECRET_KEY` for production. For local dev defaults are enough:

   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env   # Linux/macOS
   ```

3. **Run the app**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - API: http://localhost:8000  
   - Docs: http://localhost:8000/docs  
   - Database file: `./app.db` (SQLite, created on first request/startup)

4. **Quick test**

   - Register: `POST /auth/register` with JSON `{"email":"u@example.com","username":"user1","password":"password123"}`
   - Login: `POST /auth/login` with form `username=user1`, `password=password123` (or use “Authorize” in Swagger)
   - Me: `GET /auth/me` with header `Authorization: Bearer <token>`
   - Calculator: e.g. `POST /calculator/add` with JSON `{"a":1,"b":2}` and same Bearer token

## React frontend (optional)

1. **Start the backend** (from project root):

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in another terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   - UI: http://localhost:3000  
   - Vite proxies `/api` to `http://localhost:8000`, so the app calls the backend automatically.

3. **Use the UI**

   - **Register**: Create an account (email, username, password).
   - **Login**: Sign in with username and password.
   - **Calculator**: Choose operation (add/subtract/multiply/divide), enter two numbers, submit. Result is shown and added to Actions Performed.
   - **Actions Performed**: Lists all calculator operations from the current session (newest first).

   For a different backend URL (e.g. production), set `VITE_API_URL` in `frontend/.env` (e.g. `VITE_API_URL=http://localhost:8000`). Without it, the dev server uses the proxy above.

## Docker build and run

1. **Build**

   ```bash
   docker build -t fastapi-user-login .
   ```

2. **Run (env from host or file)**

   ```bash
   docker run -p 8080:8080 -e SECRET_KEY=your-secret-key -e DATABASE_URL=sqlite+aiosqlite:///./app.db fastapi-user-login
   ```

   Or with a `.env` file:

   ```bash
   docker run -p 8080:8080 --env-file .env fastapi-user-login
   ```

   App listens on port **8080** inside the container (configurable via `PORT`).

3. **Docker Compose (dev)**

   ```bash
   docker-compose up --build
   ```

   Uses `.env` and maps port 8080. Optional volume mount for `app` is in `docker-compose.yml` for development.

## Cloud Run deploy

1. **Build and push image (e.g. Google Artifact Registry)**

   ```bash
   gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG
   ```

   Or use Cloud Build with a `Dockerfile` in the repo.

2. **Deploy**

   ```bash
   gcloud run deploy SERVICE_NAME \
     --image REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG \
     --platform managed \
     --region REGION \
     --set-env-vars "SECRET_KEY=your-secret,DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname,ENVIRONMENT=production" \
     --allow-unauthenticated
   ```

   - Set `SECRET_KEY` and `DATABASE_URL` (and optionally `ACCESS_TOKEN_EXPIRE_MINUTES`, `ENVIRONMENT`) via `--set-env-vars` or Secret Manager.
   - Cloud Run sets `PORT`; the Dockerfile uses it, so no code change is needed.
   - For production, use a managed PostgreSQL instance and `postgresql+asyncpg://...` as `DATABASE_URL`.

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars in prod) | dev default |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | 30 |
| `DATABASE_URL` | Async URL: `sqlite+aiosqlite:///./app.db` or `postgresql+asyncpg://...` | SQLite |
| `ENVIRONMENT` | development / staging / production | development |
| `PORT` | Server port (Docker/Cloud Run) | 8080 |

## API summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | No | Register user (email, username, password) |
| POST | /auth/login | No | Login → JWT (form: username, password) |
| GET | /auth/me | Bearer | Current user |
| POST | /calculator/add | Bearer | JSON `{a, b}` → result |
| POST | /calculator/subtract | Bearer | JSON `{a, b}` → result |
| POST | /calculator/multiply | Bearer | JSON `{a, b}` → result |
| POST | /calculator/divide | Bearer | JSON `{a, b}` → result (400 if b=0) |
| GET | /health | No | Health check |

All calculator endpoints return JSON like: `{"operation":"add","a":1,"b":2,"result":3}`.

## License

MIT.
