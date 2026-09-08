# Smart Greenhouse

A full-stack smart greenhouse control system built for the Design Patterns 2026 course.

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Scalar API documentation

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS v4
- React Router

### Database
- PostgreSQL 16
- Docker Compose

## Prerequisites

Install the following before starting:

- Python 3.11 or newer
- Node.js 20 or newer
- Docker Desktop
- Git

You can check them with:

```powershell
python --version
node --version
docker --version
docker compose version
git --version
```

## First-time Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Ashfaqkhanshimanto/DesignPatterns-2026.git
cd DesignPatterns-2026
```

### 2. Create the local environment file

```powershell
copy .env.example .env
```

The `.env` file is for local development and must not be committed to Git.

### 3. Start PostgreSQL

Make sure Docker Desktop is running.

```powershell
docker compose up -d
```

Check that PostgreSQL is healthy:

```powershell
docker compose ps
```

### 4. Set up the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 5. Apply database migrations

Still inside the `backend` folder:

```powershell
alembic upgrade head
```

Check the current migration:

```powershell
alembic current
```

### 6. Set up the frontend

Return to the repository root and enter the frontend folder:

```powershell
cd ..
cd frontend
npm install
```

## Daily Start

The application uses three parts:

1. PostgreSQL
2. FastAPI backend
3. React frontend

### Start PostgreSQL

From the repository root:

```powershell
docker compose up -d
```

### Start the backend

Open another PowerShell window:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --app-dir src --reload
```

### Start the frontend

Open another PowerShell window:

```powershell
cd frontend
npm run dev
```

## Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Dashboard | http://localhost:5173/dashboard |
| API | http://localhost:8000 |
| Health API | http://localhost:8000/health |
| Scalar API documentation | http://localhost:8000/scalar |
| OpenAPI JSON | http://localhost:8000/openapi.json |

FastAPI Swagger documentation at `/docs` is disabled because this project uses Scalar.

## Database

PostgreSQL 16 runs through Docker Compose.

For this local setup, PostgreSQL is exposed on host port `55432`.

The backend connects to the database using the `DATABASE_URL` value from `.env`.

Phase 1 does not contain business tables. The database currently contains only the Alembic migration version table.

## Project Structure

```text
DesignPatterns-2026/
├── backend/
│   ├── alembic/
│   └── src/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── interfaces/
├── frontend/
│   └── src/
├── docs/
│   └── phases/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Course Phases

The Smart Greenhouse project is developed gradually throughout the course.

See the phase order here:

[Course phase order](docs/phases/README.md)