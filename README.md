# manufacturing-operations-platform
Educational manufacturing operations platform for production tracking, downtime analysis, quality inspections and operational intelligence.

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

## Authentication and Demonstration Users

ForgeOps uses Django authentication and role-based access through Django Groups.

The following roles are created automatically through a data migration:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

Create or update the demonstration users by running:

```bash
python manage.py seed_demo_users

The command securely asks for one password and creates these accounts:

Username	Role
operator_demo	Operator
supervisor_demo	Production Supervisor
quality_demo	Quality Specialist
engineer_demo	Manufacturing Engineer
manager_demo	Operations Manager
sysadmin_demo	System Administrator

Passwords are entered interactively and are never stored in the repository.

Authentication Routes
/accounts/login/ provides the ForgeOps login page
/accounts/logout/ securely logs out authenticated users
/ redirects users to the dashboard for their assigned role
/admin/ provides Django administration access

Users cannot access dashboards belonging to other roles.

