# ForgeOps MVP Development Backlog

## Purpose

This backlog defines the work required to build the first complete ForgeOps MVP.

Items are ordered by dependency. Work should be completed from top to bottom unless a documented decision changes the order.

## Priority Levels

- **P0:** Required for the MVP to function
- **P1:** Required for a professional MVP release
- **P2:** Useful improvement after the core workflow works
- **Future:** Outside the initial MVP

---

# Phase 1: Project Foundation

## FO-001: Create the Django Project Structure

**Priority:** P0  
**Depends on:** None

### Goal

Create the initial Django project and establish a clear application structure.

### Work

- Create the Django project.
- Create the initial Django applications.
- Configure project settings.
- Add a basic home page.
- Confirm the development server starts.
- Document the initial project structure.

### Completion Criteria

- Django starts without errors.
- The home page loads.
- The project structure is understandable.
- No secrets are committed.
- Initial setup documentation is updated.

---

## FO-002: Configure PostgreSQL

**Priority:** P0  
**Depends on:** FO-001

### Goal

Use PostgreSQL as the ForgeOps relational database.

### Work

- Install or provide PostgreSQL through the chosen development setup.
- Create the ForgeOps development database.
- Configure database environment variables.
- Connect Django to PostgreSQL.
- Run initial migrations.
- Document database setup.

### Completion Criteria

- Django connects to PostgreSQL.
- Initial migrations complete successfully.
- Credentials are not committed to GitHub.
- Database setup instructions work.

---

## FO-003: Configure Authentication and User Groups

**Priority:** P0  
**Depends on:** FO-001, FO-002

### Goal

Provide secure login, logout and role-based user groups.

### Groups

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

### Work

- Configure login and logout.
- Create the six user groups.
- Create test users for each group.
- Protect authenticated pages.
- Redirect users according to role.
- Add authentication tests.

### Completion Criteria

- Valid users can log in and log out.
- Invalid login attempts fail clearly.
- Unauthenticated users cannot access protected pages.
- Test users exist for every role.
- Authentication tests pass.

---

# Phase 2: Reference Data

## FO-004: Build the Site Model

**Priority:** P0  
**Depends on:** FO-002

### Goal

Store the fictional manufacturing site.

### Work

- Create the Site model.
- Add unique site code validation.
- Add active or inactive status.
- Register Site in Django administration.
- Add model tests.

### Completion Criteria

- A site can be created and viewed.
- Duplicate site codes are rejected.
- Required fields are enforced.
- Tests pass.

---

## FO-005: Build Product, Production Line and Shift Models

**Priority:** P0  
**Depends on:** FO-004

### Goal

Create the core reference data required for production planning.

### Work

- Create Product.
- Create ProductionLine.
- Create Shift.
- Connect ProductionLine to Site.
- Add active or inactive status.
- Add uniqueness and required-field validation.
- Register models in Django administration.
- Add tests.

### Completion Criteria

- Products, lines and shifts can be created.
- Production lines belong to a site.
- Duplicate identifiers are rejected.
- Inactive records remain stored.
- Tests pass.

---

## FO-006: Build the Downtime Reason Model

**Priority:** P0  
**Depends on:** FO-002

### Goal

Create standard downtime reason codes.

### Work

- Create DowntimeReason.
- Add unique reason code.
- Add description.
- Add active or inactive status.
- Register it in Django administration.
- Add tests.

### Completion Criteria

- Downtime reasons can be created.
- Duplicate reason codes are rejected.
- Inactive reasons cannot be used for new events.
- Tests pass.

---

# Phase 3: Production Planning

## FO-007: Build the Work Order Model

**Priority:** P0  
**Depends on:** FO-005

### Goal

Allow supervisors to define planned production.

### Work

- Create WorkOrder.
- Connect it to Product.
- Add work-order statuses.
- Add planned quantity and production date.
- Record who created it.
- Add validation.
- Add model tests.

### Completion Criteria

- Supervisors can create valid work orders.
- Work-order numbers are unique.
- Planned quantity must be greater than zero.
- Inactive products cannot be selected.
- Creation is traceable.
- Tests pass.

---

## FO-008: Build the Work Order Interface

**Priority:** P0  
**Depends on:** FO-003, FO-007

### Goal

Allow authorised supervisors to create and review work orders.

### Work

- Create the work-order list page.
- Create the work-order form.
- Create the work-order detail page.
- Add filtering by status, product and date.
- Restrict access by role.
- Add validation messages.
- Add interface tests.

### Completion Criteria

- Supervisors can create work orders.
- Unauthorised users cannot create them.
- Invalid input displays clear errors.
- Work orders can be filtered and viewed.
- Tests pass.

---

# Phase 4: Production Execution

## FO-009: Build the Production Run Model

**Priority:** P0  
**Depends on:** FO-005, FO-007

### Goal

Represent the execution of a work order.

### Work

- Create ProductionRun.
- Connect it to WorkOrder, ProductionLine and Shift.
- Assign an operator.
- Add run statuses.
- Add start and completion timestamps.
- Enforce one active run per operator.
- Add tests.

### Completion Criteria

- A work order can have production runs.
- A line, shift and operator can be assigned.
- Invalid assignments are rejected.
- An operator cannot have two active runs.
- Tests pass.

---

## FO-010: Build Production Run Assignment and Start Workflow

**Priority:** P0  
**Depends on:** FO-003, FO-009

### Goal

Allow supervisors to assign runs and operators to start them.

### Work

- Create the production-run assignment form.
- Show assigned runs to the operator.
- Add the Start Run action.
- Record the actual start time.
- Change the status to Active.
- Enforce permissions.
- Add tests.

### Completion Criteria

- Supervisors can create and assign runs.
- Operators see only assigned runs.
- Operators can start eligible runs.
- Completed or cancelled runs cannot be started.
- Tests pass.

---

## FO-011: Build the Production Entry Model

**Priority:** P0  
**Depends on:** FO-009

### Goal

Record good and rejected production quantities.

### Work

- Create ProductionEntry.
- Connect it to ProductionRun and User.
- Store good quantity.
- Store rejected quantity.
- Store notes and timestamps.
- Add quantity validation.
- Add calculated totals.
- Add tests.

### Completion Criteria

- Quantities are whole numbers.
- Negative quantities are rejected.
- At least one quantity must be greater than zero.
- Entries can only be added to active runs.
- Totals are calculated correctly.
- Tests pass.

---

## FO-012: Build the Operator Production Entry Interface

**Priority:** P0  
**Depends on:** FO-003, FO-010, FO-011

### Goal

Allow operators to record production output.

### Work

- Create the operator dashboard.
- Display the assigned active run.
- Display planned and recorded quantities.
- Add the production-entry form.
- Show recent production entries.
- Prevent entry after completion.
- Add interface and permission tests.

### Completion Criteria

- Operators can record output for their assigned active run.
- Operators cannot record against another operator's run.
- Invalid entries display clear errors.
- Totals update after saving.
- Tests pass.

---

# Phase 5: Downtime and Quality

## FO-013: Build Downtime Events

**Priority:** P0  
**Depends on:** FO-006, FO-009

### Goal

Record and calculate production downtime.

### Work

- Create DowntimeEvent.
- Connect it to ProductionRun and DowntimeReason.
- Add start and end timestamps.
- Record who opened and closed it.
- Automatically pause the run.
- Automatically reactivate the run when downtime closes.
- Calculate duration.
- Prevent multiple open downtime events.
- Add tests.

### Completion Criteria

- Operators can open downtime for an active run.
- A reason is required.
- Opening downtime pauses the run.
- Closing downtime calculates duration.
- End time cannot be earlier than start time.
- Only one downtime event can remain open.
- Tests pass.

---

## FO-014: Build the Downtime Interface

**Priority:** P0  
**Depends on:** FO-003, FO-013

### Goal

Allow operators and supervisors to manage downtime through the interface.

### Work

- Add Open Downtime action.
- Add Close Downtime action.
- Display active downtime clearly.
- Display downtime history.
- Restrict actions by role.
- Add tests.

### Completion Criteria

- Operators can open and close downtime for assigned runs.
- Supervisors can review downtime.
- Closed events cannot be closed again.
- Active downtime is clearly visible.
- Tests pass.

---

## FO-015: Build Quality Inspections

**Priority:** P0  
**Depends on:** FO-009

### Goal

Allow quality specialists to record final inspection outcomes.

### Work

- Create QualityInspection.
- Add Pending, Passed and Failed results.
- Connect it to ProductionRun and User.
- Require notes for failed inspections.
- Restrict result entry to quality users.
- Add tests.

### Completion Criteria

- Quality specialists can record inspection results.
- Unauthorised users cannot alter results.
- Failed inspections require notes.
- Inspector and completion time are recorded.
- Tests pass.

---

## FO-016: Build the Quality Inspection Interface

**Priority:** P0  
**Depends on:** FO-003, FO-015

### Goal

Provide a clear inspection workflow.

### Work

- Create the inspection list.
- Create the inspection form.
- Display production context.
- Highlight failed inspections.
- Prevent unauthorised editing.
- Add tests.

### Completion Criteria

- Quality users can find runs requiring inspection.
- Passed and Failed results can be recorded.
- Failed results are clearly visible.
- Permission tests pass.

---

# Phase 6: Completion and Audit History

## FO-017: Build the Production Run Completion Workflow

**Priority:** P0  
**Depends on:** FO-010, FO-011, FO-013, FO-015

### Goal

Allow supervisors to complete eligible production runs.

### Work

- Add supervisor review page.
- Display final quantities.
- Display downtime.
- Display inspection results.
- Check completion requirements.
- Record completion timestamp.
- Lock completed operational records.
- Add tests.

### Completion Criteria

A run cannot be completed unless:

- Production quantities exist.
- No downtime event remains open.
- A passed final inspection exists.
- The user has supervisor permission.

Completed runs cannot accept new production entries.

---

## FO-018: Build Audit Events

**Priority:** P0  
**Depends on:** Core production models

### Goal

Record important system actions.

### Work

- Create AuditEvent.
- Record user, action, time, record type and identifier.
- Create audit events for critical workflows.
- Prevent normal editing and deletion.
- Add tests.

### Completion Criteria

- Important actions create audit records.
- Audit records identify the user and affected record.
- Normal users cannot edit audit records.
- Tests pass.

---

## FO-019: Build the Audit History Interface

**Priority:** P1  
**Depends on:** FO-003, FO-018

### Goal

Allow authorised users to review system activity.

### Work

- Create the audit-history page.
- Add filters for user, action, date and record type.
- Enforce read-only access.
- Restrict access by role.
- Add tests.

### Completion Criteria

- Authorised users can review audit history.
- Filters work correctly.
- No edit or delete actions are available.
- Unauthorised access is rejected.

---

# Phase 7: Analytics and Dashboard

## FO-020: Build Dashboard Calculations

**Priority:** P0  
**Depends on:** FO-011, FO-013, FO-015, FO-017

### Goal

Calculate the main production metrics.

### Metrics

- Planned quantity
- Good quantity
- Rejected quantity
- Total recorded quantity
- Remaining quantity
- Completion percentage
- Rejection rate
- Total downtime
- Active run count
- Completed run count
- Failed inspection count

### Completion Criteria

- Every formula has automated tests.
- Zero totals do not cause calculation errors.
- Results use stored records.
- Known test data produces expected values.

---

## FO-021: Build the Operations Manager Dashboard

**Priority:** P0  
**Depends on:** FO-003, FO-020

### Goal

Present production performance to managers.

### Work

- Add metric cards.
- Add date filtering.
- Add line filtering.
- Add product filtering.
- Add shift filtering.
- Add planned versus actual chart.
- Add downtime summary.
- Highlight runs requiring attention.
- Enforce read-only access.
- Add tests.

### Completion Criteria

- Dashboard metrics are accurate.
- Filters work correctly.
- Failed inspections are visible.
- Managers cannot alter production records.
- Tests pass.

---

# Phase 8: MVP Quality and Delivery

## FO-022: Create Synthetic Demonstration Data

**Priority:** P1  
**Depends on:** Core models

### Goal

Provide realistic fictional information for demonstrations.

### Work

- Create one fictional site.
- Create production lines.
- Create products.
- Create shifts.
- Create downtime reasons.
- Create demonstration users.
- Create work orders and production history.
- Document the fictional nature of the data.

### Completion Criteria

- Demo accounts represent all roles.
- The database contains enough data to demonstrate dashboards.
- No employer information is included.

---

## FO-023: Complete Critical Automated Tests

**Priority:** P0  
**Depends on:** All MVP features

### Goal

Ensure the core workflow is reliable.

### Required Coverage

- Authentication
- Permissions
- Work-order validation
- Production-run assignment
- Production quantities
- Downtime calculations
- Inspection results
- Completion restrictions
- Dashboard formulas
- Audit-event creation

### Completion Criteria

- Critical tests pass.
- Tests use synthetic data.
- Failed tests are fixed before release.

---

## FO-024: Add Docker and Docker Compose

**Priority:** P1  
**Depends on:** Working local MVP

### Goal

Make the application reproducible.

### Work

- Create the Django Dockerfile.
- Add PostgreSQL through Docker Compose.
- Add environment-variable support.
- Add startup instructions.
- Confirm a clean installation works.

### Completion Criteria

- The application and database start using one documented command.
- Database data persists using a volume.
- Secrets are not embedded in Docker files.

---

## FO-025: Add GitHub Actions

**Priority:** P1  
**Depends on:** FO-023

### Goal

Automatically run project checks.

### Work

- Install dependencies.
- Run migrations.
- Run automated tests.
- Fail the workflow when tests fail.
- Run on pushes and pull requests.

### Completion Criteria

- GitHub Actions runs successfully.
- Failed tests produce a failed workflow.
- The workflow is documented.

---

## FO-026: Prepare the MVP Release

**Priority:** P1  
**Depends on:** All MVP issues

### Goal

Produce a professional portfolio release.

### Work

- Complete the README.
- Add screenshots.
- Add architecture and ER diagrams.
- Add installation instructions.
- Add demo credentials.
- Add testing instructions.
- Add known limitations.
- Deploy the application.
- Record a two-minute demonstration.
- Create a versioned release.

### Completion Criteria

- The deployment is accessible.
- Demo credentials work.
- The README accurately describes the project.
- The complete workflow can be demonstrated.
- The educational disclaimer is visible.
- A versioned MVP release exists.

---

# Future Backlog

The following are outside the initial MVP:

- Batch traceability
- Machine records
- Defect categories
- Deviation workflow
- Corrective actions
- REST API
- Machine simulator
- Redis and Celery
- Prometheus
- Grafana
- Nginx
- Advanced analytics
- OPC UA simulation
- Cloud infrastructure automation

---

# MVP Release Boundary

The MVP is complete when a recruiter can:

1. Log in as a supervisor.
2. Create and assign a work order.
3. Log in as an operator.
4. Start a production run.
5. Record output and downtime.
6. Log in as a quality specialist.
7. Record a passed inspection.
8. Complete the run as a supervisor.
9. View updated metrics as a manager.
10. Review the audit history.
11. See automated tests passing.
12. Run or access the deployed application.