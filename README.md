# FoodHub

FoodHub turns photographed restaurant menus into structured dish data and
personalized, explainable recommendations. It enriches dishes through a local
cache, TheMealDB, and a batched AI fallback, then evaluates the resulting food
facts against each user's saved profile and current-meal preferences.

Key capabilities:

- Registration, login, and database-backed sessions
- User profiles, allergies, dietary restrictions, religious requirements, and
  taste preferences
- Upload of 1–5 menu images per scan
- English, Simplified Chinese, and French interfaces and dish presentation
- Live TheMealDB matching and batched fallback for unknown dishes
- English canonical fields for matching and localized fields for display
- A database-backed demo mode that makes no external AI requests

## 1. Repository Structure

```text
foodhub/
├── backend/                 FastAPI, recommendation rules, database, and tests
│   ├── api/                 HTTP routes
│   ├── core/                Configuration, logging, security, and localization
│   ├── migrations/          Alembic history; do not delete old migrations
│   ├── schemas/             Frontend and Backend B data contracts
│   ├── services/            AI, TheMealDB, database, and recommendation services
│   └── tests/
├── frontend/                React, TypeScript, Vite, and Tailwind CSS
├── docs/                    Architecture, API, integration, and presentation docs
├── .env.example             Backend environment-variable template
└── README.md
```

## 2. Prerequisites

- Windows 10/11, or another OS that supports Python, Node.js, and MySQL
- Python 3.11, the version used for this project's tests
- MySQL 8
- Node.js `20.19+` or `22.12+`
- npm, installed with Node.js
- Git, when publishing to GitHub

If PowerShell reports that `npm` is not recognized, install Node.js, close and
reopen PowerShell, then verify the installation:

```powershell
node --version
npm --version
```

## 3. Create the MySQL Database

Run the following commands as an administrator in MySQL Workbench or the MySQL
command-line client:

```sql
CREATE DATABASE foodhub
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'foodhub'@'localhost'
  IDENTIFIED BY 'foodhub_local_password';

GRANT ALL PRIVILEGES ON foodhub.* TO 'foodhub'@'localhost';
FLUSH PRIVILEGES;
```

Use a different password in any shared or production environment. If the
password contains characters such as `@`, `:`, or `/`, URL-encode it in the
SQLAlchemy connection URL.

## 4. Configure Backend Environment Variables

The backend reads configuration from `.env` in the repository root:

```powershell
cd D:\APP\foodhub
Copy-Item .env.example .env
```

At minimum, verify the database connection in `.env`:

```dotenv
FOODHUB_DATABASE_URL=mysql+asyncmy://foodhub:foodhub_local_password@localhost:3306/foodhub?charset=utf8mb4
```

### Demo configuration

Demo mode does not require an OpenAI API key and does not upload the selected
image to any external service:

```dotenv
FOODHUB_DEMO_AVAILABLE=true
FOODHUB_LIVE_SCAN_ENABLED=false
FOODHUB_OPENAI_API_KEY=
FOODHUB_OPENAI_MODEL=
```

### Live scan configuration

Live menu scanning requires an OpenAI API key and a model already validated
with the Backend B menu-understanding contract:

```dotenv
FOODHUB_DEMO_AVAILABLE=true
FOODHUB_LIVE_SCAN_ENABLED=true
FOODHUB_OPENAI_API_KEY=
FOODHUB_OPENAI_MODEL=your_valid_model_id
```

Put the real key only in the local, uncommitted `.env` file. Never place API
keys in the frontend, README, screenshots, or Git history. The frontend never
receives the key or model ID.

The free TheMealDB endpoint uses the following development key by default:

```dotenv
FOODHUB_THEMEALDB_API_KEY=1
```

## 5. Install and Start the Backend

Creating the virtual environment inside the D-drive project keeps it off the C
drive and makes the interpreter easy to reuse from PyCharm:

```powershell
cd D:\APP\foodhub\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation scripts, call the virtual-environment
interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Apply the database migrations:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

The result should show the current migration head, for example:

```text
0005_demo_menu_templates (head)
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend URLs:

- Health check: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI specification: `http://127.0.0.1:8000/openapi.json`

A 404 response at `http://127.0.0.1:8000/` is expected. The customer-facing
application is served by the frontend.

Suggested PyCharm run configuration:

- Interpreter: `D:\APP\foodhub\backend\.venv\Scripts\python.exe`
- Working directory: `D:\APP\foodhub\backend`
- Module: `uvicorn`
- Parameters: `main:app --reload`

## 6. Install and Start the Frontend

Open a second PowerShell window:

```powershell
cd D:\APP\foodhub\frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:3000`.

During local development, Vite proxies `/api` to
`http://127.0.0.1:8000`, so a frontend environment file is normally not
required.

If the frontend and backend are deployed at different origins:

```powershell
Copy-Item .env.example .env.local
```

Then set:

```dotenv
VITE_API_BASE_URL=https://your-backend.example.com/api
```

Every `VITE_` variable is included in the browser bundle. Never use one for a
secret.

## 7. User Flow

1. Register an account and choose English, Simplified Chinese, or French.
2. Save allergies, dietary restrictions, religious requirements, and taste
   preferences.
3. On the scan page, select one of the following modes:
   - **Demo mode:** loads a fixed menu from MySQL and makes no AI request.
   - **Live scan:** uploads 1–5 menu images and runs the full analysis pipeline.
4. Review dish names, prices, explicit ingredients, reference ingredients, AI
   inferences, and allergen evidence.
5. Set current-meal preferences and call `/api/recommendations` to rerank the
   dishes.

The pipeline deliberately separates source evidence, canonical matching data,
and localized display data:

```text
original/menu evidence        Restaurant source evidence
canonical_*_en                English values for database and rule matching
translated_*/evidence.display Localized values for the customer interface
```

To see a newly added localization patch, rescan the menu or reload the demo.
Previously saved `menu_id` responses are not rewritten in place.

## 8. Dish Resolution and Recommendation Pipeline

1. Check AI fallback dishes already cached in the local SQL database.
2. Query TheMealDB using the English canonical dish name.
3. Collect every dish missed by both the local cache and TheMealDB.
4. Send all misses to Backend B in one batch to reduce token overhead.
5. Save the returned fallback food facts for faster future resolution.
6. Map ingredient evidence to allergens and run deterministic recommendation
   rules against the user's profile and current-meal preferences.
7. Localize the display fields and return explainable `match`, `neutral`, or
   `avoid` results to the frontend.

TheMealDB responses are not persisted. Users, preferences, fallback dishes,
menu analyses, and demo templates are stored in MySQL.

## 9. Test Before Submission

Backend checks:

```powershell
cd D:\APP\foodhub\backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m alembic current
```

Frontend checks:

```powershell
cd D:\APP\foodhub\frontend
npm run lint
npm run build
```

## 10. Troubleshooting

- **401 Unauthorized:** log in again and replace the Bearer token in Swagger.
- **422 Unprocessable Entity:** check request-field names, email format, and
  password requirements.
- **502 Bad Gateway:** verify the OpenAI key, model ID, and network connection
  used by live scan. Demo mode does not need a key.
- **MySQL connection failure:** check the MySQL80 service, database credentials,
  and the URL in `.env`.
- **`npm` is not recognized:** install Node.js and reopen PowerShell.
- **Backend root returns 404:** use `/docs` for the API or port `3000` for the
  customer interface.
