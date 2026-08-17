# manufacturing-operations-platform

Educational manufacturing operations platform for production tracking, downtime analysis, quality inspections, and operational intelligence.

## Local Development Setup

### Requirements

- Python 3.12+
- PostgreSQL 18
- Postgres.app on macOS

### Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Update `.env` with private local development values.

Apply migrations:

```bash
python manage.py migrate
```

Start the local development server:

```bash
python manage.py runserver
```

ForgeOps is then available at:

```text
http://127.0.0.1:8000/
```

## Docker Development Setup

ForgeOps can also run using Docker and Docker Compose.

The containerised development environment contains:

```text
web -> Django 6.0 development server
db  -> PostgreSQL 18
```

The Docker PostgreSQL database is separate from the host PostgreSQL database.

### Requirements

- Docker Desktop
- Docker Compose

Verify Docker:

```bash
docker --version
docker compose version
```

### Build the Django Image

```bash
docker compose build
```

### Start ForgeOps

```bash
docker compose up
```

Or start the services in the background:

```bash
docker compose up -d
```

The Compose configuration waits for PostgreSQL to become healthy before starting Django.

ForgeOps is available at:

```text
http://127.0.0.1:8000/
```

### Apply Database Migrations

For a new Docker PostgreSQL volume:

```bash
docker compose exec web python manage.py migrate
```

### Run Django System Checks

```bash
docker compose exec web python manage.py check
```

### Check for Migration Drift

```bash
docker compose exec web python manage.py makemigrations --check --dry-run
```

### Run the Core Automated Test Suite

```bash
docker compose exec web python manage.py test core -v 2
```

The FO-024 verified Docker regression baseline is:

```text
Ran 330 tests
OK
```

### Stop ForgeOps

```bash
docker compose down
```

The PostgreSQL data is stored in the named Docker volume:

```text
manufacturing-operations-platform_postgres_data
```

Normal `docker compose down` removes the containers and network but preserves this volume.

The following command also removes the PostgreSQL volume and its stored Docker development data:

```bash
docker compose down -v
```

Only use the `-v` form when intentionally resetting the Docker database.

## Authentication and Demonstration Users

ForgeOps uses Django authentication and role-based access through Django Groups.

The following roles are created automatically through a data migration:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

Create or update the demonstration users locally by running:

```bash
python manage.py seed_demo_users
```

For the Docker environment, run:

```bash
docker compose exec web python manage.py seed_demo_users
```

The command securely asks for one password and creates these accounts:

| Username | Role |
| --- | --- |
| `operator_demo` | Operator |
| `supervisor_demo` | Production Supervisor |
| `quality_demo` | Quality Specialist |
| `engineer_demo` | Manufacturing Engineer |
| `manager_demo` | Operations Manager |
| `sysadmin_demo` | System Administrator |

Passwords are entered interactively and are never stored in the repository.

All demonstration and test data must remain synthetic.

## Authentication Routes

```text
/accounts/login/    ForgeOps login page
/accounts/logout/   Logout endpoint
/                   Redirects authenticated users to their assigned dashboard
/admin/             Django administration
```

Users cannot access dashboards belonging to other roles