# Smart Issue Tracker & Root Cause Analyzer

A full-stack issue management platform for tracking bugs, tasks, workflow status, team ownership, audit history, and dashboard analytics.

The project is built with a React frontend, Django REST Framework backend, JWT authentication, PostgreSQL support, Docker, GitHub Actions CI, and Render deployment configuration.

## Tech Stack

- Frontend: ReactJS, Vite, React Router, Axios, Chart.js
- Backend: Python, Django, Django REST Framework, Simple JWT
- Database: SQLite for local development, PostgreSQL for production/Docker
- DevOps: Docker, Docker Compose, GitHub Actions, Render, Gunicorn, Nginx
- Analytics: Dashboard metrics, rule-based insights, TF-IDF similarity with scikit-learn

## Key Features

- 3 role-based user flows: Admin, Developer, and Reporter
- JWT login and protected frontend routes
- Public registration for Developer and Reporter roles
- Admin-only user and full issue management access
- Issue workflow: Open -> Assigned -> In Progress -> Resolved -> Closed/Reopened
- Issue CRUD, assignment, comments, search, filtering, and sorting
- Audit logs for create, update, and delete actions
- Role-based issue visibility and API permissions
- Dashboard charts for status, priority, workload, and resolution metrics
- Root-cause insights using recurring category analysis and TF-IDF similarity
- Swagger and ReDoc API documentation
- Dockerized frontend, backend, and PostgreSQL setup
- CI workflow for backend checks, migrations, frontend build, and Docker validation

## Project Structure

```text
.
+-- backend/              # Django REST API
|   +-- issue_tracker/    # Django project settings and URLs
|   +-- tracker/          # Users, issues, comments, audit logs, API logic
+-- frontend/             # React + Vite frontend
|   +-- src/              # Pages, components, auth, API client
+-- .github/workflows/    # GitHub Actions CI
+-- docker-compose.yml    # Full-stack Docker setup
+-- render.yaml           # Render deployment blueprint
```

## API Modules

- `POST /api/token/` - login and receive JWT tokens
- `POST /api/token/refresh/` - refresh access token
- `POST /api/register/register/` - register Reporter or Developer
- `/api/issues/` - issue CRUD, dashboard, and root-cause endpoints
- `/api/comments/` - issue comments
- `/api/audit/` - audit log access
- `/api/users/` - user listing and filtering
- `/swagger/` and `/redoc/` - API documentation

## Local Setup

### Backend

```bash
python -m venv backend/venv
backend/venv/Scripts/activate
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py runserver
```

Backend runs at:

```text
http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Environment Variables

The backend can run with SQLite by default. To use PostgreSQL, create a `.env` file using `backend/.env.example`:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=smart_issue_tracker
POSTGRES_USER=tracker_user
POSTGRES_PASSWORD=tracker_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

For the frontend, set the API base URL if needed:

```env
VITE_API_BASE_URL=http://localhost:8000/api/
```

## Docker Setup

Run the complete stack with PostgreSQL:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`
- Swagger docs: `http://localhost:8000/swagger/`

Create an admin user inside the backend container:

```bash
docker compose exec backend python manage.py createsuperuser
```

## PostgreSQL Migration

To move local SQLite data into PostgreSQL:

```bash
python backend/manage.py dumpdata --exclude contenttypes --exclude auth.permission --indent 2 > data.json
python backend/manage.py migrate
python backend/manage.py loaddata data.json
```

On Windows PowerShell, the helper script can generate the SQLite dump:

```powershell
.\backend\scripts\migrate_sqlite_to_postgres.ps1
```

## CI/CD

GitHub Actions runs on pushes and pull requests to `main` or `master`.

The workflow checks:

- Django project configuration
- PostgreSQL migrations
- React production build
- Docker Compose configuration
- Docker image builds
- Optional Render deployment hooks on `main` push

## Render Deployment

The repository includes `render.yaml` for deploying:

- PostgreSQL database: `smart-issue-tracker-db`
- Backend Docker service: `smart-issue-tracker-backend`
- Frontend static service: `smart-issue-tracker-frontend`

Important Render variables:

- Backend `DATABASE_URL` is provided by Render PostgreSQL
- Backend `CORS_ALLOWED_ORIGINS` should point to the frontend URL
- Backend `CSRF_TRUSTED_ORIGINS` should point to the backend URL
- Frontend `VITE_API_BASE_URL` should point to the backend `/api/` URL

## Notes

- API root is available under `/api/`.
- Health check endpoint is available at `/health/`.
- React uses `VITE_API_BASE_URL` when provided, otherwise it uses local Django in development and `/api/` in production.
