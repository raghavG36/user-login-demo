# Learning Guide: Adding New Features (Beginner-Friendly)

This guide helps you understand how this project works and how to add new features. You'll learn where to look, what to change, and how to test. No prior FastAPI experience is required.

---

## Who this guide is for

- You are new to FastAPI or this codebase.
- You want to add a new API endpoint or change existing behavior.
- You prefer step-by-step instructions and clear file paths.

---

## Before you start

### 1. Get the app running

From the project root (the folder that contains `app/` and `requirements.txt`):

```bash
# Create and activate a virtual environment (once)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # Linux/macOS

# Install dependencies (once)
pip install -r requirements.txt

# Copy environment file (once)
copy .env.example .env           # Windows
# cp .env.example .env           # Linux/macOS

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API:** http://localhost:8000  
- **Interactive docs (Swagger):** http://localhost:8000/docs  

If you can open the docs page and see "FastAPI User Login & Calculator", you're ready.

### 2. What you'll need

- **Python 3.10+** (check with `python --version`).
- **A code editor** (e.g. VS Code, Cursor).
- **5–10 minutes** to read the "Project layout" and "How a request is handled" sections before making changes.

---

## Glossary: terms used in this guide

| Term | Meaning |
|------|--------|
| **Endpoint** | One URL + HTTP method (e.g. `POST /auth/login`). What the client calls. |
| **Router** | A group of endpoints (e.g. all `/auth/*` routes live in the auth router). |
| **Schema** | A Pydantic model that describes the **shape** of JSON (request body or response). It also validates input (e.g. "password must be at least 8 characters"). |
| **Service** | Functions that contain the **business logic** (e.g. "check password", "compute result"). They don't know about HTTP or status codes. |
| **Dependency** | Something FastAPI provides to your route automatically (e.g. "current user" or "database session"). You use `Depends(...)` to ask for it. |
| **JWT** | A token that proves the user is logged in. The client sends it in the header `Authorization: Bearer <token>`. Protected routes need a valid JWT. |
| **Protected route** | An endpoint that requires the user to be logged in (valid JWT). Unauthorized requests get 401. |

---

## Project layout: where everything lives

```
app/
├── main.py                 # App entry: CORS, routers, /health
├── api/
│   ├── auth/               # Login, register, "who am I?"
│   │   ├── router.py       # Routes: POST /auth/register, POST /auth/login, GET /auth/me
│   │   ├── schemas.py      # Request/response shapes (e.g. UserRegisterRequest)
│   │   └── service.py      # Logic: create user, check password, create JWT
│   └── calculator/         # Add, subtract, multiply, divide
│       ├── router.py       # Routes: POST /calculator/add, etc.
│       ├── schemas.py      # CalculatorOperands, CalculatorResult
│       └── service.py      # Logic: add(a, b), multiply(a, b), etc.
├── core/
│   ├── config.py           # Settings from .env (SECRET_KEY, DATABASE_URL, ...)
│   └── security.py         # Password hashing, JWT create/decode
└── db/
    ├── models.py           # User table (id, email, username, hashed_password, ...)
    ├── session.py          # Database connection and "get_db" dependency
    └── base.py             # SQLAlchemy base (used by models)
```

When you add a feature:

- **New request/response shape** → `schemas.py`
- **New logic (e.g. change password, new math operation)** → `service.py`
- **New URL (e.g. PATCH /auth/me/password)** → `router.py`
- **New table or column** → `db/models.py` (and sometimes a DB migration; this project creates tables on startup)

---

## How a request is handled (big picture)

Example: **POST /auth/login** (user logs in with username and password).

1. **Router** (`app/api/auth/router.py`) receives the request. It uses `OAuth2PasswordRequestForm` so FastAPI reads `username` and `password` from the form.
2. **Service** (`app/api/auth/service.py`) is called: `authenticate_user(session, username, password)`. It looks up the user and checks the password.
3. **Security** (`app/core/security.py`): Password is checked with `verify_password(plain, hashed)`. If valid, a JWT is created with `create_access_token(user.id)`.
4. **Router** returns the token in the response (e.g. `{"access_token": "...", "token_type": "bearer"}`).

For a **protected** endpoint (e.g. POST /calculator/add):

1. **Router** declares `current_user: User = Depends(get_current_user)`. FastAPI then:
   - Reads `Authorization: Bearer <token>` from the request
   - Decodes the JWT (in `get_current_user`) and loads the user from the database
   - If the token is missing or invalid, it returns **401** before your route runs
2. Your route runs only when the user is valid; you use `current_user` and call the **service** for the actual logic.

So: **router** = HTTP and auth, **service** = business logic, **schemas** = data shape and validation.

---

## How user login works (step-by-step)

This section walks through exactly what happens when a user logs in (e.g. from the Swagger UI or the React frontend) and which modules or libraries are involved at each step.

### What the client sends

The client calls **POST /auth/login** with a **form body** (not JSON):

- `username` – the user’s username  
- `password` – the user’s plain-text password  

This format is the standard **OAuth2 “password” flow**: credentials are sent as form fields so tools like Swagger “Authorize” and many frontends can use it.

### Step-by-step flow

| Step | Where | What happens |
|------|--------|----------------|
| 1 | **FastAPI** | The request hits the app. The auth router is mounted at `/auth`, so **POST /auth/login** is handled by the `login` function in `app/api/auth/router.py`. |
| 2 | **FastAPI + python-multipart** | The route declares `form_data: OAuth2PasswordRequestForm = Depends()`. FastAPI (with the **python-multipart** library) parses the request body as form data and fills `form_data.username` and `form_data.password`. |
| 3 | **FastAPI + SQLAlchemy** | The route also declares `session: AsyncSession = Depends(get_db)`. FastAPI calls the **get_db** dependency (`app/db/session.py`), which yields an async database session. **SQLAlchemy** (with **aiosqlite** or **asyncpg**) provides that session. |
| 4 | **Auth service** | The router calls `authenticate_user(session, form_data.username, form_data.password)` in `app/api/auth/service.py`. |
| 5 | **SQLAlchemy** | Inside `authenticate_user`, the code runs `select(User).where(User.username == username)` and executes it with `session.execute()`. The **User** model is defined in `app/db/models.py`. The database returns the user row (or nothing). |
| 6 | **bcrypt** | If a user was found, the service calls `verify_password(password, user.hashed_password)` from `app/core/security.py`. That function uses **bcrypt** to compare the plain password with the stored hash. If they don’t match (or user is inactive), the service returns `None`. |
| 7 | **Router** | If `authenticate_user` returns `None`, the router raises **HTTPException(401, "Incorrect username or password")** and the response is 401. No token is returned. |
| 8 | **python-jose + config** | If the user is valid, the router calls `create_token_for_user(user)` in the auth service. That calls `create_access_token(subject=user.id)` in `app/core/security.py`. **python-jose** (JWT) builds a token with payload `{"sub": user_id, "exp": expiry_time, "iat": issued_at}` and signs it with **SECRET_KEY** and **ALGORITHM** from `app/core/config.py` (loaded by **pydantic-settings** from `.env`). |
| 9 | **Pydantic** | The router returns a **TokenResponse** (from `app/api/auth/schemas.py`): `access_token`, `token_type="bearer"`, `expires_in_minutes`. **Pydantic** serializes this to JSON. The client receives the token and typically stores it to send later as `Authorization: Bearer <token>`. |

### After login: using the token on protected routes

When the client calls a protected endpoint (e.g. **GET /auth/me** or **POST /calculator/add**), it sends the header:

```text
Authorization: Bearer <access_token>
```

| Step | Where | What happens |
|------|--------|----------------|
| 1 | **FastAPI** | The route has `current_user: User = Depends(get_current_user)`. FastAPI runs the **get_current_user** dependency first. |
| 2 | **FastAPI security** | **OAuth2PasswordBearer** (from FastAPI) reads the `Authorization` header and extracts the token. It’s defined in `app/api/auth/router.py` as `oauth2_scheme`. |
| 3 | **python-jose** | **get_current_user** calls `decode_access_token(token)` in `app/core/security.py`. **python-jose** verifies the signature and expiry; if invalid or expired, it raises **JWTError** and the code returns **401**. |
| 4 | **Auth service + SQLAlchemy** | If the token is valid, the payload’s `sub` (user id) is used to call `get_user_by_id(session, user_id)` in the auth service. The user is loaded from the database again (so we have the latest user row). If not found or inactive, **401** is returned. |
| 5 | **Router** | If everything is OK, **get_current_user** returns the **User** object. FastAPI injects it as `current_user`, and your route runs with the logged-in user. |

### Modules and libraries used for login

| Module / library | Role in login |
|------------------|----------------|
| **FastAPI** | Defines the **POST /auth/login** route, parses form via **OAuth2PasswordRequestForm**, provides **Depends(get_db)** and **Depends(get_current_user)**, returns JSON response. |
| **python-multipart** | Lets FastAPI parse `application/x-www-form-urlencoded` body so **OAuth2PasswordRequestForm** gets `username` and `password`. Without it, form-based login would fail. |
| **OAuth2PasswordRequestForm** (FastAPI) | Standard dependency that reads username and password from the request form; used by Swagger “Authorize” and OAuth2 clients. |
| **OAuth2PasswordBearer** (FastAPI) | Reads `Authorization: Bearer <token>` from the request; used by **get_current_user** to get the JWT. |
| **Pydantic** | **TokenResponse** and **UserResponse** schemas define and serialize the login response and user data. |
| **pydantic-settings** | Loads **SECRET_KEY**, **ALGORITHM**, **ACCESS_TOKEN_EXPIRE_MINUTES** from `.env` so JWT creation and validation use the same config. |
| **SQLAlchemy** (async) | Provides the **User** model and async session; used to look up user by username (login) and by id (get_current_user). |
| **aiosqlite / asyncpg** | Async database drivers; SQLAlchemy uses them to run queries (SQLite locally, PostgreSQL in production). |
| **bcrypt** | In **app/core/security.py**: hashes passwords at registration (**get_password_hash**) and verifies them at login (**verify_password**). Passwords are never stored in plain text. |
| **python-jose** | In **app/core/security.py**: creates the JWT after successful login (**create_access_token**) and decodes/validates it on protected routes (**decode_access_token**). |

### Files involved in login

| File | Purpose |
|------|--------|
| `app/api/auth/router.py` | Defines **POST /auth/login**, **get_current_user**, and **OAuth2PasswordBearer**. |
| `app/api/auth/service.py` | **authenticate_user** (look up user, verify password), **create_token_for_user**, **get_user_by_id**. |
| `app/api/auth/schemas.py` | **TokenResponse** (access_token, token_type, expires_in_minutes), **UserResponse**. |
| `app/core/security.py` | **verify_password**, **get_password_hash** (bcrypt), **create_access_token**, **decode_access_token** (python-jose). |
| `app/core/config.py` | **SECRET_KEY**, **ALGORITHM**, **ACCESS_TOKEN_EXPIRE_MINUTES** (pydantic-settings). |
| `app/db/models.py` | **User** model (username, hashed_password, is_active, etc.). |
| `app/db/session.py` | **get_db** dependency that provides the async database session. |

---

## Key libraries (simplified)

| Library | What it does here | What you need to know |
|---------|--------------------|------------------------|
| **FastAPI** | Defines routes, runs validation, injects dependencies (e.g. current user). | You add `@router.get/post/patch(...)` and use `Depends(get_current_user)` for protected routes. |
| **Pydantic** | Defines "schemas": request/response models with types and rules (min length, etc.). | You add classes that inherit `BaseModel` and use `Field(...)` for validation. |
| **SQLAlchemy** | Talks to the database (async). Models are in `db/models.py`; session is provided by `get_db`. | You use `session` in services to run queries and `session.commit()` to save. |
| **python-jose** | Creates and decodes JWT tokens. | Used in `core/security.py`; you use `create_access_token` and `decode_access_token` when needed. |
| **bcrypt** | Hashes passwords (never store plain passwords). | Used in `core/security.py`; you use `get_password_hash` and `verify_password` in auth logic. |

You don't need to memorize everything. When you add a feature, you'll usually:

- Add or reuse a **schema** (Pydantic) for the request/response.
- Add a **service** function that does the work (and uses `get_db` if you need the database).
- Add a **route** that calls the service and uses `Depends(get_current_user)` if the endpoint must be logged-in only.

---

## How to add a new feature (general steps)

Use this checklist for any new endpoint:

1. **Decide the URL and method** (e.g. `PATCH /auth/me/password`). Decide if it must be protected (user must be logged in).
2. **Open the right module** (e.g. auth → `app/api/auth/`, calculator → `app/api/calculator/`).
3. **Schemas:** In `schemas.py`, add a Pydantic model for the request body (and response if it's different from existing ones).
4. **Service:** In `service.py`, add a function that does the work. If you need the database, make the function `async` and take `session: AsyncSession`; get the session in the router with `Depends(get_db)`.
5. **Router:** In `router.py`, add a new route. Use `Depends(get_current_user)` if the endpoint is protected. Call your service and return the response (or `Response(status_code=204)` for no body).
6. **Test:** Open http://localhost:8000/docs, try the new endpoint (use "Authorize" for protected routes).

---

## Function requirement 1: Change password

**What you're building:** A logged-in user can change their password by sending their **current password** and a **new password**. The API checks the current password and, if correct, saves the new one (hashed).

**Endpoint:** `PATCH /auth/me/password` (requires JWT).  
**Request body:** `{ "current_password": "...", "new_password": "..." }`  
**Response:** 204 No Content on success. 401 if not logged in or current password is wrong.

### Step 1: Add the request schema

**File:** `app/api/auth/schemas.py`

Add a new class (e.g. after `UserLoginRequest`):

```python
class ChangePasswordRequest(BaseModel):
    """Request to change password (current + new)."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
```

You already have `from pydantic import BaseModel, EmailStr, Field` at the top; if not, add `Field` to the import.

### Step 2: Add the service function

**File:** `app/api/auth/service.py`

- Import: `from app.core.security import get_password_hash, verify_password`
- Add an async function:

```python
async def change_password(
    session: AsyncSession,
    user_id: int,
    current_password: str,
    new_password: str,
) -> bool:
    """Update user password if current_password is correct. Returns True on success, False otherwise."""
    user = await get_user_by_id(session, user_id)
    if user is None or not user.is_active:
        return False
    if not verify_password(current_password, user.hashed_password):
        return False
    user.hashed_password = get_password_hash(new_password)
    await session.commit()
    return True
```

You already have `get_user_by_id` in this file; use it to load the user.

### Step 3: Add the route

**File:** `app/api/auth/router.py`

- Add to imports: `Response` from `fastapi`, and `ChangePasswordRequest` from `app.api.auth.schemas`, and `change_password` from `app.api.auth.service`.
- Add the route (e.g. after the `me` endpoint):

```python
@router.patch("/me/password", status_code=204)
async def change_password_route(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Change current user's password. Requires valid JWT and correct current password."""
    success = await change_password(
        session, current_user.id, body.current_password, body.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Response(status_code=204)
```

So: you need both `Depends(get_current_user)` and `Depends(get_db)` in the same route.

### Step 4: Test

1. Open http://localhost:8000/docs.
2. Log in: **POST /auth/login** with username/password (form or body). Copy the `access_token` from the response.
3. Click **Authorize**, paste the token (with or without "Bearer " depending on the UI), then Authorize.
4. Call **PATCH /auth/me/password** with body: `{"current_password": "your_real_password", "new_password": "newpassword123"}`.
5. You should get **204** with no body. Then try logging in with the new password to confirm.

---

## Function requirement 2: Calculator power (exponent)

**What you're building:** A new calculator operation: **power** (base^exponent). Same style as add/subtract: client sends two numbers, server returns the result. Must be logged in (JWT).

**Endpoint:** `POST /calculator/power` (requires JWT).  
**Request body:** `{ "a": 2, "b": 10 }` (a = base, b = exponent).  
**Response:** `{ "operation": "power", "a": 2, "b": 10, "result": 1024 }`

### Step 1: Schemas

**File:** `app/api/calculator/schemas.py`

No change. Reuse `CalculatorOperands` (fields `a` and `b`) and `CalculatorResult` (operation, a, b, result).

### Step 2: Add the service function

**File:** `app/api/calculator/service.py`

Add:

```python
def power(operands: CalculatorOperands) -> CalculatorResult:
    """Return a ** b (base to the power of exponent)."""
    return CalculatorResult(
        operation="power",
        a=operands.a,
        b=operands.b,
        result=operands.a ** operands.b,
    )
```

### Step 3: Add the route

**File:** `app/api/calculator/router.py`

- Import `power` from the service (e.g. `from app.api.calculator.service import ... power`).
- Add (same pattern as `add` / `subtract`):

```python
@router.post("/power", response_model=CalculatorResult)
async def power_route(
    body: CalculatorOperands,
    current_user: User = Depends(get_current_user),
):
    """Compute base^exponent. Requires JWT."""
    return power(body)
```

### Step 4: Test

1. Open http://localhost:8000/docs and **Authorize** with a token (from login).
2. Call **POST /calculator/power** with body: `{"a": 2, "b": 10}`.
3. You should get `{"operation": "power", "a": 2, "b": 10, "result": 1024}`.

---

## Quick reference: copy-paste patterns

### New request body schema (Pydantic)

```python
class MyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0)
```

### New protected POST route (needs login)

```python
@router.post("/my-path", response_model=MyResponse)
async def my_route(
    body: MyRequest,
    current_user: User = Depends(get_current_user),
):
    result = my_service_function(body)  # or await if async
    return result
```

### New protected route that needs the database

```python
@router.patch("/me/something", status_code=204)
async def my_route(
    body: MyRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    success = await my_service(session, current_user.id, body)
    if not success:
        raise HTTPException(status_code=401, detail="Not allowed")
    return Response(status_code=204)
```

### Return 401 Unauthorized

```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Message for the client",
    headers={"WWW-Authenticate": "Bearer"},
)
```

---

## Summary

| What you added | Endpoint | Files to edit |
|----------------|----------|----------------|
| **Change password** | PATCH /auth/me/password | auth/schemas.py, auth/service.py, auth/router.py |
| **Calculator power** | POST /calculator/power | calculator/service.py, calculator/router.py |

**Next steps:**

1. Implement **Requirement 1** (change password) first—it uses schemas, service, router, and the database.
2. Then implement **Requirement 2** (power)—it reuses schemas and is a small addition.
3. Try adding your own idea (e.g. another calculator operation or a simple "update my username" endpoint) using the same pattern: schema → service → route → test in Swagger.

If something doesn’t work: check that the server was restarted after edits (or that `--reload` is running), that you Authorize in Swagger for protected routes, and that request bodies match the schema (e.g. field names and types).
