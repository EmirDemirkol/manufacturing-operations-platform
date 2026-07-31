# ForgeOps Phase 0 Planning

## Problem Statement

Manufacturing teams need a structured way to record production output, rejected units, downtime, quality inspections and operational performance.

This information can become fragmented across spreadsheets, paper records and separate systems, making it difficult to understand production performance or investigate what happened during a specific production run.

ForgeOps will provide a fictional manufacturing operations platform where authorised users can record, review and analyse production activity.

ForgeOps is an educational portfolio project using entirely synthetic data. It will not control machinery or claim to be suitable for real regulated manufacturing.

## Objectives

- Record work orders and production runs.
- Record good and rejected quantities.
- Record downtime events and reasons.
- Record basic quality inspection results.
- Provide role-based access.
- Display useful production metrics.
- Maintain an audit history.
- Demonstrate Django, PostgreSQL, testing, Docker and deployment skills.

## MVP Scope

The first working version will include:

- User login and logout
- Role-based permissions
- Production lines
- Products
- Shifts
- Work orders
- Production runs
- Good and rejected quantity recording
- Downtime recording
- Basic pass or fail inspections
- Production dashboard
- Audit history
- Synthetic demonstration data

## Stakeholders

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

## Main Risks

- The project becomes too large.
- Too many technologies are added too early.
- The database is poorly designed.
- Permissions are implemented incorrectly.
- Dashboard calculations are inaccurate.
- AI-generated code is used without understanding.
- Testing and documentation are postponed.

## MVP Workflow

1. A supervisor creates a work order.
2. The supervisor assigns it to a production line and shift.
3. An operator starts the production run.
4. The operator records good and rejected quantities.
5. The operator records downtime and selects a reason.
6. A quality specialist records a pass or fail inspection.
7. The supervisor completes the production run.
8. A manager views the results on a dashboard.
9. Important actions are recorded in the audit history.

## Roadmap

### Phase 0
Discovery and planning.

### Phase 1
Requirements, user stories, BPMN, database design and wireframes.

### Phase 2
Django and PostgreSQL project foundation.

### Phase 3
Core production workflow.

### Phase 4
Downtime, quality inspections and audit history.

### Phase 5
Dashboard, testing and MVP deployment.

### Later Phases
Batch traceability, advanced analytics, REST API, Docker, CI/CD and monitoring.