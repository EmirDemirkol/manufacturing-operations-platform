# ForgeOps Core User Stories

## Purpose

These user stories define the main actions required for the ForgeOps MVP.

Each story follows this format:

As a [user role], I want [action], so that [business benefit].

---

## US-01: User Login

**As a registered user, I want to log in securely so that I can access the features allowed for my role.**

### Acceptance Criteria

- The user can enter a username and password.
- Valid credentials allow the user to log in.
- Invalid credentials display an error message.
- The user is redirected to an appropriate page after login.
- Unauthenticated users cannot access protected pages.
- The user can log out securely.

---

## US-02: Manage System Configuration

**As a system administrator, I want to configure products, production lines, shifts and downtime reasons so that the system contains the information required for production recording.**

### Acceptance Criteria

- The administrator can create a product.
- The administrator can create a production line.
- The administrator can create a shift.
- The administrator can create a downtime reason.
- Required fields cannot be left blank.
- Duplicate identifiers are rejected where uniqueness is required.
- Users without administrator permission cannot access configuration pages.
- Important configuration changes are added to the audit history.

---

## US-03: Create a Work Order

**As a production supervisor, I want to create a work order for a product so that planned production can be recorded and assigned.**

### Acceptance Criteria

- The supervisor can select a product.
- The supervisor can enter a unique work-order number.
- The supervisor can enter a planned quantity.
- The planned quantity must be greater than zero.
- The supervisor can enter a planned production date.
- A new work order begins with the status Planned.
- Duplicate work-order numbers are rejected.
- Users without the correct permission cannot create work orders.
- Work-order creation is recorded in the audit history.

---

## US-04: Assign a Production Run

**As a production supervisor, I want to assign a work order to a production line and shift so that an operator knows where and when production should occur.**

### Acceptance Criteria

- The supervisor can select an existing work order.
- The supervisor can select a production line.
- The supervisor can select a shift.
- The supervisor can assign an operator.
- The assigned work order must not be cancelled.
- The same work order cannot be assigned incorrectly to conflicting active runs.
- The production run begins with the status Not Started.
- The assigned operator can view the production run.
- The assignment is recorded in the audit history.

---

## US-05: Start a Production Run

**As an operator, I want to start an assigned production run so that the system records when production begins.**

### Acceptance Criteria

- The operator can view production runs assigned to them.
- The operator can start a run with the status Not Started.
- The system records the actual start date and time.
- The production-run status changes to Active.
- A completed or cancelled run cannot be started.
- An operator cannot start a run assigned to another operator without permission.
- Starting the run creates an audit event.

---

## US-06: Record Production Output

**As an operator, I want to record good and rejected quantities so that production performance can be measured.**

### Acceptance Criteria

- The operator can enter a good quantity.
- The operator can enter a rejected quantity.
- Quantities must be whole numbers.
- Quantities cannot be negative.
- At least one quantity must be greater than zero.
- Production entries can only be added to an active production run.
- The system calculates the total recorded quantity.
- The system identifies the user and time of each entry.
- The production entry is included in dashboard calculations.
- Creating the production entry generates an audit event.

---

## US-07: Record Downtime

**As an operator, I want to record when a production line stops and select a reason so that downtime can be measured and investigated.**

### Acceptance Criteria

- The operator can open a downtime event for an active production run.
- The operator must select a downtime reason.
- The system records the downtime start time.
- The operator can close the downtime event.
- The system records the downtime end time.
- The system calculates the downtime duration.
- The end time cannot be earlier than the start time.
- A closed downtime event cannot be closed again.
- Downtime is included in dashboard calculations.
- Opening and closing downtime creates audit events.

---

## US-08: Record a Quality Inspection

**As a quality specialist, I want to record a pass or fail inspection so that the quality status of a production run is visible.**

### Acceptance Criteria

- The quality specialist can select a production run.
- The quality specialist can record a Pass or Fail result.
- The quality specialist can add inspection notes.
- The inspection records the user, date and time.
- Only authorised quality users can complete an inspection.
- A failed inspection is clearly visible to supervisors and managers.
- The inspection result cannot be blank.
- Creating or changing the inspection creates an audit event.

---

## US-09: Complete a Production Run

**As a production supervisor, I want to complete a production run so that final results can be reviewed and protected from unrestricted changes.**

### Acceptance Criteria

- The supervisor can view the total good quantity.
- The supervisor can view the total rejected quantity.
- The supervisor can view total downtime.
- The supervisor can view completed inspection results.
- Open downtime events must be closed before completion.
- The supervisor can complete an active production run.
- The system records the completion date and time.
- The status changes to Completed.
- Operators cannot add new production entries after completion.
- Completion creates an audit event.

---

## US-10: View the Production Dashboard

**As an operations manager, I want to compare planned and actual production results so that I can identify performance problems.**

### Acceptance Criteria

- The dashboard displays planned quantity.
- The dashboard displays good quantity.
- The dashboard displays rejected quantity.
- The dashboard displays total recorded quantity.
- The dashboard displays completion percentage.
- The dashboard displays rejection rate.
- The dashboard displays total downtime.
- The dashboard displays failed-inspection count.
- The manager can filter results by date.
- The manager can filter results by production line.
- The manager can filter results by product.
- The manager can filter results by shift.
- Dashboard calculations are based on stored production records.
- Unauthorised users cannot access management-level dashboards.

---

## US-11: Review Audit History

**As a system administrator, I want to review important user actions so that changes to production records are traceable.**

### Acceptance Criteria

- The audit history records the user who performed the action.
- The audit history records the action performed.
- The audit history records the date and time.
- The audit history identifies the affected record.
- Audit records cannot be edited by normal users.
- Only authorised users can access the audit-history page.
- Audit records can be filtered by user.
- Audit records can be filtered by action type.
- Audit records can be filtered by date.

---

## MVP User Story Priority

### Must Have

- US-01: User Login
- US-02: Manage System Configuration
- US-03: Create a Work Order
- US-04: Assign a Production Run
- US-05: Start a Production Run
- US-06: Record Production Output
- US-07: Record Downtime
- US-08: Record a Quality Inspection
- US-09: Complete a Production Run
- US-10: View the Production Dashboard
- US-11: Review Audit History

## Definition of Done for a User Story

A user story is complete when:

- All acceptance criteria are satisfied.
- Role permissions are enforced.
- Server-side validation is included.
- Relevant automated tests pass.
- Audit events are created where required.
- Error messages are clear.
- Documentation is updated.
- The feature is reviewed and can be demonstrated.