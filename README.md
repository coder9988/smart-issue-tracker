# Smart Issue Tracker & Root Cause Analyzer

Full-stack issue tracker built with Django, Django REST Framework, PostgreSQL, React, JWT authentication, and rule-based analytics.

## Features

- Single JWT login for Admin, Developer, and Reporter roles
- Public registration for Reporter and Developer only
- Admin accounts created through Django admin or `createsuperuser`
- Role-based dashboards and issue visibility
- Issue workflow: Open -> Assigned -> In Progress -> Resolved -> Closed, with Reopened
- Assignment, comments, audit logs, filtering, and sorting
- Dashboard charts and rule-based root cause insights
- Swagger API documentation

## Backend Setup

1. Create a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run migrations and create a superuser:
   ```bash
   python backend/manage.py migrate
   python backend/manage.py createsuperuser
   ```
4. Start backend server:
   ```bash
   python backend/manage.py runserver
   ```

### PostgreSQL

The backend defaults to SQLite for local development. To switch to PostgreSQL, configure a `.env` file with:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

To move existing SQLite data into PostgreSQL:

```bash
python backend/manage.py dumpdata --exclude contenttypes --exclude auth.permission --indent 2 > data.json
# Configure POSTGRES_* variables, then run:
python backend/manage.py migrate
python backend/manage.py loaddata data.json
```

On Windows PowerShell, you can also generate the SQLite dump with:

```powershell
.\backend\scripts\migrate_sqlite_to_postgres.ps1
```

## Frontend Setup

1. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start frontend development server:
   ```bash
   npm run dev
   ```

## Docker

Run the full stack with PostgreSQL:

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`
- Swagger docs: `http://localhost:8000/swagger/`

Create an admin user inside Docker with:

```bash
docker compose exec backend python manage.py createsuperuser
```

## GitHub Actions

The workflow in `.github/workflows/ci.yml` runs on pushes and pull requests. It checks:

- Django setup against a PostgreSQL service
- Django migrations on PostgreSQL
- React production build
- Docker Compose config and Docker image builds

## Render Deployment

The repository includes `render.yaml` for a Render Blueprint deployment:

- PostgreSQL database: `smart-issue-tracker-db`
- Backend Docker web service: `smart-issue-tracker-backend`
- Frontend static web service: `smart-issue-tracker-frontend`

Render should provide `DATABASE_URL` to the backend from the managed PostgreSQL database. The backend Docker entrypoint runs:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn issue_tracker.wsgi:application
```

After deploying, update these Render environment variables if your generated service URLs differ from the names in `render.yaml`:

- Backend `CORS_ALLOWED_ORIGINS`: frontend URL, for example `https://smart-issue-tracker-frontend.onrender.com`
- Backend `CSRF_TRUSTED_ORIGINS`: backend URL, for example `https://smart-issue-tracker-backend.onrender.com`
- Frontend `VITE_API_BASE_URL`: backend API URL, for example `https://smart-issue-tracker-backend.onrender.com/api/`

Create an admin user from the Render backend shell:

```bash
python manage.py createsuperuser
```

## Notes

- API root is served under `/api/`.
- React uses `VITE_API_BASE_URL` when provided, otherwise it calls local Django in development and `/api/` in production.
- GitHub Actions can be added after the Docker/PostgreSQL flow is finalized.
