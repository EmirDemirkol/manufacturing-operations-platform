# ForgeOps Decision Log

This document records important business and technical decisions for the ForgeOps project.

---

## ADR-001: Work Orders Can Have Multiple Production Runs

**Decision:** One work order may have multiple production runs.

**Reason:** A work order could be split across different shifts, operators or production lines.

For the MVP, the normal demonstration workflow will use one production run per work order, but the database will support multiple runs.

**Database relationship:**

One WorkOrder has many ProductionRuns.

---

## ADR-002: One Active Run Per Operator

**Decision:** An operator may have only one active production run at a time.

**Reason:** This keeps production responsibility clear and prevents an operator from recording output against the wrong run.

The restriction may be reviewed in a later version.

---

## ADR-003: One Required Final Inspection

**Decision:** Every production run must have at least one completed final quality inspection before it can be completed.

The required final inspection must have the result:

- Passed

A pending or failed inspection prevents normal production-run completion.

Additional optional inspections may be introduced later.

---

## ADR-004: Production-Entry Corrections

**Decision:** Production entries may be edited by an authorised user while the production run is active.

Every edit must create an audit event.

After the production run is completed:

- Production entries are locked.
- Normal editing is prohibited.
- A future correction workflow will use traceable adjustment records.

The advanced correction workflow is outside the MVP.

---

## ADR-005: Downtime Automatically Pauses Production

**Decision:** Opening a downtime event automatically changes the production-run status from Active to Paused.

Closing the downtime event changes the run back to Active.

Only one downtime event may remain open for a production run at a time.

A production run cannot be completed while downtime remains open.

---

## ADR-006: Completion Percentage Uses Good Quantity

**Decision:** Completion percentage will use good units rather than total recorded units.

**Formula:**

```text
Completion percentage = total good quantity / planned quantity × 100

Reason: Rejected units do not satisfy the planned production requirement.

The dashboard will display rejected quantities separately.

ADR-007: Supervisors May Record Production Output

Decision: A production supervisor may record quantities on behalf of an operator.

This should be treated as an exception rather than the normal workflow.

When a supervisor records production output:

The system records the supervisor as the user.
The supervisor must provide a reason or note.
An audit event is created.
ADR-008: Overnight Shift Representation

Decision: Shifts will store a start time and end time.

When the end time is earlier than or equal to the start time, the shift is treated as crossing midnight.

Example:

Night Shift
Start: 22:00
End: 06:00

The shift begins on one calendar date and ends on the following calendar date.

Production runs will store full actual start and completion timestamps separately from the shift definition.

Decision Summary
One work order may have multiple production runs.
An operator may have only one active run.
At least one passed final inspection is required.
Production entries can be edited before completion, with auditing.
Open downtime automatically pauses the run.
Completion percentage uses good quantity.
Supervisors can record output as an audited exception.
Shifts with an earlier end time cross midnight.

Save with `Command + S`, then run:

```bash
git status
git add docs/decision-log.md
git commit -m "docs: resolve initial database design decisions"
git push

After this, the next step is drawing the first ForgeOps ER diagram from these approved entities and relationships.

---

## ADR-009: Awaiting Review Production-Run Status

**Decision:** Production runs will support an `Awaiting Review` status.

The complete status list is:

- Not Started
- Active
- Paused
- Awaiting Review
- Completed
- Cancelled

When the operator finishes recording production, the run moves from Active to Awaiting Review.

The supervisor can then:

- Complete the run if all requirements are satisfied.
- Return it to Active if further work or correction is required.

---

## ADR-010: Completed Inspections Are Immutable

**Decision:** A completed quality inspection will not be edited through the normal workflow.

If a run fails inspection and is later corrected:

1. The failed inspection remains in the history.
2. The production run returns to Active.
3. A quality specialist creates a new inspection.
4. The run can only be completed after a later inspection passes.

This provides better traceability than overwriting the failed result.

---

## ADR-011: Remaining Quantity and Overproduction

**Decision:** Remaining quantity will never display as a negative number.

```text
Remaining quantity = maximum of 0 and planned quantity - good quantity

Overproduction will be calculated separately:

Overproduction quantity = maximum of 0 and good quantity - planned quantity

Completion percentage may exceed 100% when good production exceeds the planned quantity.

ADR-012: Work-Order Status Transitions

Decision: Work orders will follow these normal status transitions:

Planned → Released → In Progress → Completed

A work order may also move to Cancelled before completion when cancellation is permitted.

Rules:

Planned means the work order has been created.
Released means it has been approved for production assignment.
In Progress means at least one production run has started.
Completed means all associated production runs are completed.
Cancelled work orders cannot receive new production runs.
Completed work orders cannot be cancelled through the normal workflow.
Phase 1 Consistency Review

The initial design review resolved the following issues:

Awaiting Review is now an official production-run status.
Failed quality inspections remain in the historical record.
Corrected runs require a new inspection rather than editing an old result.
Remaining quantity cannot become negative.
Overproduction is measured separately.
Work-order status transitions are now defined.