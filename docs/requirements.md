# ForgeOps Requirements

## Purpose

This document defines the functional and non-functional requirements for the ForgeOps Manufacturing Operations Intelligence Platform.

ForgeOps is an educational portfolio application using entirely synthetic manufacturing data.

The system will not control machinery and will not be represented as validated software for real manufacturing, medical-device, pharmaceutical or safety-critical operations.

---

# 1. Functional Requirements

Functional requirements describe what the system must allow users to do.

## Authentication and User Access

### FR-01: User Authentication

The system shall allow registered users to log in using a valid username and password.

### FR-02: User Logout

The system shall allow authenticated users to log out securely.

### FR-03: Protected Pages

The system shall prevent unauthenticated users from accessing protected application pages.

### FR-04: Role-Based Permissions

The system shall restrict actions and information according to the user's assigned role.

The initial roles are:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

---

## System Configuration

### FR-05: Product Management

The system shall allow authorised administrators to create, view and update fictional products.

Each product shall include:

- Unique product code
- Product name
- Description
- Active or inactive status

### FR-06: Production-Line Management

The system shall allow authorised administrators to create, view and update production lines.

Each production line shall include:

- Unique line code
- Line name
- Site
- Active or inactive status

### FR-07: Shift Management

The system shall allow authorised administrators to configure production shifts.

Each shift shall include:

- Shift name
- Start time
- End time
- Active or inactive status

### FR-08: Downtime-Reason Management

The system shall allow authorised administrators to configure downtime reasons.

Each downtime reason shall include:

- Unique reason code
- Reason name
- Description
- Active or inactive status

---

## Work Orders

### FR-09: Work-Order Creation

The system shall allow production supervisors to create work orders.

Each work order shall include:

- Unique work-order number
- Product
- Planned quantity
- Planned production date
- Status
- Created by
- Creation date and time

### FR-10: Work-Order Validation

The system shall reject a work order when:

- The work-order number already exists.
- The planned quantity is zero or negative.
- A required field is missing.
- The selected product is inactive.

### FR-11: Work-Order Status

The system shall support the following work-order statuses:

- Planned
- Released
- In Progress
- Completed
- Cancelled

### FR-12: Work-Order Cancellation

The system shall allow an authorised production supervisor to cancel an eligible work order.

The system shall record who cancelled it and when.

---

## Production Runs

### FR-13: Production-Run Creation

The system shall allow a production supervisor to create a production run from an eligible work order.

### FR-14: Production-Run Assignment

The system shall allow the supervisor to assign the production run to:

- A production line
- A shift
- An operator

### FR-15: Assigned Production View

The system shall allow operators to view production runs assigned to them.

Operators shall not normally see production runs assigned to other operators.

### FR-16: Start Production Run

The system shall allow an assigned operator or authorised supervisor to start a production run.

When a run is started, the system shall:

- Record the actual start date and time.
- Change the production-run status to Active.
- Record the user who started the run.

### FR-17: Production-Run Status

The system shall support the following production-run statuses:

- Not Started
- Active
- Paused
- Completed
- Cancelled

### FR-18: Complete Production Run

The system shall allow an authorised supervisor to complete an active production run.

Before completion:

- All open downtime events must be closed.
- Required production information must be present.
- Required quality inspections must be completed.

When completed:

- The completion date and time shall be recorded.
- The status shall change to Completed.
- Normal production entry shall be disabled.

---

## Production Output

### FR-19: Production-Entry Creation

The system shall allow an authorised operator to record production quantities against an active production run.

Each production entry shall include:

- Good quantity
- Rejected quantity
- Production run
- Recorded by
- Recorded date and time

### FR-20: Quantity Validation

The system shall enforce the following quantity rules:

- Quantities must be whole numbers.
- Quantities cannot be negative.
- At least one entered quantity must be greater than zero.
- Entries can only be added to an active production run.

### FR-21: Production Totals

The system shall calculate:

- Total good quantity
- Total rejected quantity
- Total recorded quantity
- Remaining planned quantity
- Completion percentage
- Rejection rate

---

## Downtime

### FR-22: Open Downtime Event

The system shall allow an authorised operator to open a downtime event for an active production run.

The user must select a downtime reason.

### FR-23: Close Downtime Event

The system shall allow an authorised operator or supervisor to close an open downtime event.

### FR-24: Downtime Duration

The system shall calculate downtime duration using the event start time and end time.

The downtime end time shall not be earlier than its start time.

### FR-25: Open Downtime Restriction

A downtime event that has already been closed shall not be closed again through the normal workflow.

---

## Quality Inspections

### FR-26: Inspection Creation

The system shall allow an authorised quality specialist to create an inspection for a production run.

### FR-27: Inspection Result

The system shall support the following inspection results:

- Pending
- Passed
- Failed

### FR-28: Inspection Details

Each inspection shall include:

- Production run
- Inspection result
- Notes
- Completed by
- Completion date and time

### FR-29: Failed Inspection Visibility

Failed inspections shall be clearly visible to authorised supervisors, quality specialists, engineers and managers.

### FR-30: Inspection Permissions

Only authorised quality users shall be allowed to record or change an inspection result.

---

## Dashboard and Reporting

### FR-31: Production Dashboard

The system shall provide an operational dashboard displaying:

- Planned quantity
- Good quantity
- Rejected quantity
- Total recorded quantity
- Remaining quantity
- Completion percentage
- Rejection rate
- Total downtime
- Active production runs
- Completed production runs
- Failed inspections

### FR-32: Dashboard Filters

The dashboard shall allow authorised users to filter results by:

- Date range
- Production line
- Product
- Shift

### FR-33: Dashboard Permissions

Management-level dashboards shall only be accessible to authorised users.

### FR-34: Dashboard Data Source

Dashboard calculations shall use stored production, downtime and inspection records.

Values shall not be manually entered directly into the dashboard.

---

## Audit History

### FR-35: Audit-Event Creation

The system shall create audit events for significant actions, including:

- User or role creation
- Configuration changes
- Work-order creation
- Work-order cancellation
- Production-run assignment
- Production-run start
- Production quantity entry
- Downtime opening
- Downtime closing
- Quality-inspection creation
- Quality-inspection update
- Production-run completion
- Authorised record correction

### FR-36: Audit-Event Information

Each audit event shall include:

- User
- Action
- Date and time
- Record type
- Record identifier
- Relevant description

### FR-37: Audit-History Access

Only authorised users shall be able to view audit history.

### FR-38: Audit-History Protection

Audit records shall not be editable or deletable through the normal application interface.

### FR-39: Audit Filtering

Authorised users shall be able to filter audit records by:

- User
- Date
- Action type
- Record type

---

# 2. Non-Functional Requirements

Non-functional requirements describe the expected quality, security, usability and maintainability of the system.

## Security

### NFR-01: Password Security

The system shall use Django's secure password-handling system.

Plain-text passwords shall never be stored.

### NFR-02: Secret Management

Passwords, secret keys and database credentials shall be stored using environment variables.

Secrets shall not be committed to GitHub.

### NFR-03: Server-Side Authorisation

Every protected action shall be checked on the server.

Hiding buttons in the interface shall not be treated as sufficient security.

### NFR-04: CSRF Protection

The system shall use CSRF protection for forms that create or modify data.

### NFR-05: Input Validation

All user-submitted data shall be validated on the server before it is saved.

---

## Data Integrity

### NFR-06: Database Constraints

The database shall use appropriate constraints to prevent invalid records.

Examples include:

- Unique work-order numbers
- Unique product codes
- Non-negative quantities
- Required relationships
- Valid status values

### NFR-07: Referential Integrity

The system shall prevent records from referring to products, production lines, users or work orders that do not exist.

### NFR-08: Completed Record Protection

Completed production runs shall be protected against unrestricted editing.

Any authorised correction shall be traceable.

### NFR-09: Transaction Safety

Operations that update multiple related records shall avoid leaving the database in a partially updated state.

---

## Performance

### NFR-10: Page Response

Normal application pages should load within approximately three seconds under demonstration-level usage.

### NFR-11: Dashboard Performance

The MVP dashboard should calculate and display results within approximately five seconds using the demonstration dataset.

### NFR-12: Database Query Efficiency

Frequently used pages shall avoid unnecessary or repeated database queries.

---

## Usability

### NFR-13: Clear Navigation

Users shall be able to identify the main actions available for their role.

### NFR-14: Clear Validation Messages

When user input is rejected, the system shall display a clear explanation.

### NFR-15: Consistent Interface

Pages shall use consistent layouts, buttons, terminology and status labels.

### NFR-16: Responsive Design

The application shall be usable on desktop and tablet-sized screens.

Mobile optimisation is desirable but is not an MVP requirement.

### NFR-17: Accessible Forms

Forms shall include clear labels, required-field indicators and understandable error messages.

---

## Reliability

### NFR-18: Error Handling

Unexpected application errors shall not expose secret information, source code or database credentials.

### NFR-19: Valid State Transitions

The system shall prevent invalid workflow transitions.

Examples include:

- Starting a completed run
- Completing a cancelled run
- Recording output against an inactive run
- Closing downtime that is already closed

### NFR-20: Repeatable Calculations

The same stored data shall produce the same dashboard results.

---

## Maintainability

### NFR-21: Modular Structure

The Django application shall be divided into clear modules based on responsibility.

### NFR-22: Code Readability

Code shall use meaningful names and consistent formatting.

### NFR-23: Documentation

Important workflows, architecture decisions and setup instructions shall be documented.

### NFR-24: Decision Log

Major technical and business decisions shall be recorded in `docs/decision-log.md`.

### NFR-25: Dependency Control

Third-party dependencies shall only be added when they provide a clear project benefit.

---

## Testing

### NFR-26: Automated Tests

Critical workflows shall have automated tests.

Testing shall cover:

- Authentication
- Permissions
- Work-order creation
- Production-run creation
- Quantity validation
- Downtime calculations
- Quality-inspection results
- Production-run completion
- Dashboard calculations
- Audit-event creation

### NFR-27: Failed Test Protection

A failed automated test shall prevent a change from being treated as complete.

### NFR-28: Test Data

Tests shall use fictional data created specifically for the test environment.

---

## Deployment and Portability

### NFR-29: Environment Separation

Development and deployed environments shall use separate configuration where required.

### NFR-30: Docker Support

The completed MVP shall support containerised execution using Docker.

### NFR-31: Reproducible Setup

A new developer shall be able to run ForgeOps using documented setup instructions.

### NFR-32: Continuous Integration

GitHub Actions shall run automated checks when code is pushed or a pull request is opened.

---

## Privacy and Ethical Use

### NFR-33: Synthetic Data

ForgeOps shall use entirely synthetic manufacturing, product, batch and user information.

### NFR-34: Confidentiality

The repository shall not contain confidential employer documents, targets, screenshots, process information or customer data.

### NFR-35: Educational Disclaimer

The README shall state that ForgeOps is:

- An educational portfolio project
- Based on fictional data
- Not validated for regulated manufacturing
- Not intended to control machinery
- Not suitable for safety-critical operations

---

# 3. MVP Requirement Priority

## Must Have

- Authentication
- Role-based permissions
- Products
- Production lines
- Shifts
- Downtime reasons
- Work orders
- Production runs
- Production quantities
- Downtime events
- Basic quality inspections
- Production dashboard
- Audit history
- Validation
- Automated tests
- Synthetic demonstration data

## Should Have

- Better search and filtering
- Improved dashboard charts
- CSV export
- Correction workflow
- Detailed audit comparisons

## Could Have Later

- Batch traceability
- Defects
- Deviations
- Corrective actions
- REST API
- Machine simulator
- Advanced analytics
- Monitoring

## Excluded from the MVP

- Real machinery integration
- SAP integration
- OPC UA integration
- Machine learning
- Microservices
- Kubernetes
- Real regulated-manufacturing use