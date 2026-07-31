# ForgeOps Database Design

## Purpose

This document defines the initial database entities, attributes, relationships and integrity rules for the ForgeOps MVP.

The database will use PostgreSQL.

ForgeOps will use Django's built-in User and Group models for authentication and role management.

---

# 1. Core Entities

## User

Provided by Django's authentication system.

Represents a person who can log into ForgeOps.

Important information includes:

- ID
- Username
- Password hash
- First name
- Last name
- Email
- Active status
- Assigned groups
- Date joined

Django Groups will represent the ForgeOps roles:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

---

## Site

Represents a fictional manufacturing location.

### Attributes

- ID
- Site code
- Site name
- Location
- Active status
- Created date and time
- Updated date and time

### Rules

- Site code must be unique.
- Site name is required.

For the MVP, ForgeOps will use one fictional site, but the structure will support additional sites later.

---

## Product

Represents a fictional product manufactured at the site.

### Attributes

- ID
- Product code
- Product name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Product code must be unique.
- Product name is required.
- Inactive products cannot be selected for new work orders.

---

## ProductionLine

Represents a manufacturing line.

### Attributes

- ID
- Site
- Line code
- Line name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Each production line belongs to one site.
- Line code must be unique.
- Inactive lines cannot be selected for new production runs.

---

## Shift

Represents a scheduled working period.

### Attributes

- ID
- Shift name
- Start time
- End time
- Active status
- Created date and time
- Updated date and time

### Rules

- Shift name must be unique.
- Start time and end time are required.
- Inactive shifts cannot be selected for new production runs.

Example shifts:

- Day Shift
- Evening Shift
- Night Shift

---

## WorkOrder

Represents planned production for a product.

### Attributes

- ID
- Work-order number
- Product
- Planned quantity
- Planned production date
- Status
- Created by
- Created date and time
- Updated date and time
- Cancelled by
- Cancelled date and time

### Status Values

- Planned
- Released
- In Progress
- Completed
- Cancelled

### Rules

- Work-order number must be unique.
- Planned quantity must be greater than zero.
- Each work order relates to one product.
- Cancelled work orders cannot be used for new production runs.
- The selected product must be active.

---

## ProductionRun

Represents the execution of a work order on a production line during a shift.

### Attributes

- ID
- Work order
- Production line
- Shift
- Assigned operator
- Status
- Actual start date and time
- Actual completion date and time
- Created by
- Created date and time
- Updated date and time

### Status Values

- Not Started
- Active
- Paused
- Completed
- Cancelled

### Rules

- Each production run belongs to one work order.
- Each production run occurs on one production line.
- Each production run occurs during one shift.
- Each production run is assigned to one operator.
- A completed production run cannot accept new production entries.
- A cancelled production run cannot be started.
- The production line and shift must be active.

---

## ProductionEntry

Represents a quantity recorded during an active production run.

### Attributes

- ID
- Production run
- Good quantity
- Rejected quantity
- Recorded by
- Recorded date and time
- Notes

### Rules

- Each production entry belongs to one production run.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- At least one quantity must be greater than zero.
- Quantities must be whole numbers.
- Production entries can only be created for active production runs.

### Calculated Values

- Entry total = good quantity + rejected quantity
- Run good total = sum of all good quantities
- Run rejected total = sum of all rejected quantities
- Run total = run good total + run rejected total

Calculated values should normally be derived from production entries rather than stored separately.

---

## DowntimeReason

Represents a standard reason for a production stoppage.

### Attributes

- ID
- Reason code
- Reason name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Reason code must be unique.
- Reason name is required.
- Inactive reasons cannot be selected for new downtime events.

Example reasons:

- Equipment fault
- Material shortage
- Quality inspection
- Planned maintenance
- Operator unavailable
- Changeover

---

## DowntimeEvent

Represents a period during which production stopped.

### Attributes

- ID
- Production run
- Downtime reason
- Start date and time
- End date and time
- Opened by
- Closed by
- Notes
- Created date and time
- Updated date and time

### Rules

- Each downtime event belongs to one production run.
- Each downtime event has one downtime reason.
- Downtime can only be opened for an active production run.
- End time cannot be earlier than start time.
- A closed downtime event cannot be closed again.
- A production run cannot be completed while it has open downtime.

### Calculated Value

Downtime duration = end date and time minus start date and time.

The duration should be calculated from timestamps rather than manually entered.

---

## QualityInspection

Represents a basic quality check performed against a production run.

### Attributes

- ID
- Production run
- Result
- Notes
- Completed by
- Completed date and time
- Created date and time
- Updated date and time

### Result Values

- Pending
- Passed
- Failed

### Rules

- Each inspection belongs to one production run.
- Only authorised quality users can record the result.
- A completed result must be Passed or Failed.
- Failed results must be visible to authorised supervisors and managers.
- Required inspections must be completed before the production run is completed.

---

## AuditEvent

Represents an important action performed in ForgeOps.

### Attributes

- ID
- User
- Action type
- Record type
- Record identifier
- Description
- Event date and time

### Example Action Types

- Created
- Updated
- Assigned
- Started
- Completed
- Cancelled
- Opened
- Closed
- Corrected

### Rules

- Audit events are created automatically.
- Audit events cannot be edited through the normal application interface.
- Audit events cannot be deleted through the normal application interface.
- An audit event may reference a record without using a direct database relationship to every possible entity.

---

# 2. Relationships

## Site Relationships

- One Site has many ProductionLines.
- One ProductionLine belongs to one Site.

## Product Relationships

- One Product has many WorkOrders.
- One WorkOrder belongs to one Product.

## Work-Order Relationships

- One WorkOrder may have one or more ProductionRuns.
- One ProductionRun belongs to one WorkOrder.

The MVP will normally use one production run per work order, but the database should not unnecessarily prevent future split runs.

## Production-Run Relationships

One ProductionRun belongs to:

- One WorkOrder
- One ProductionLine
- One Shift
- One assigned User

One ProductionRun can have many:

- ProductionEntries
- DowntimeEvents
- QualityInspections

## Production-Entry Relationships

- One ProductionRun has many ProductionEntries.
- One ProductionEntry belongs to one ProductionRun.
- One User may record many ProductionEntries.

## Downtime Relationships

- One DowntimeReason may be used by many DowntimeEvents.
- One ProductionRun may have many DowntimeEvents.
- One DowntimeEvent belongs to one ProductionRun.
- One DowntimeEvent uses one DowntimeReason.

## Quality Relationships

- One ProductionRun may have many QualityInspections.
- One QualityInspection belongs to one ProductionRun.
- One quality User may complete many QualityInspections.

## Audit Relationships

- One User may generate many AuditEvents.
- Each AuditEvent records one action performed by one User.
- AuditEvents identify affected records using record type and record identifier.

---

# 3. Relationship Summary

```text
Site
└── ProductionLine
    └── ProductionRun
        ├── ProductionEntry
        ├── DowntimeEvent
        │   └── DowntimeReason
        └── QualityInspection

Product
└── WorkOrder
    └── ProductionRun

Shift
└── ProductionRun

User
├── ProductionRun assignment
├── ProductionEntry recording
├── DowntimeEvent opening and closing
├── QualityInspection completion
└── AuditEvent

4. Initial Integrity Rules
Product codes must be unique.
Production-line codes must be unique.
Work-order numbers must be unique.
Downtime-reason codes must be unique.
Planned quantities must be greater than zero.
Good and rejected quantities cannot be negative.
Production entries can only be added to active production runs.
Downtime end times cannot occur before downtime start times.
Completed production runs cannot accept new operational records.
Open downtime events must be closed before production-run completion.
Required quality inspections must be completed before production-run completion.
Inactive reference records cannot be selected for new operational records.
Audit records cannot be changed through standard application workflows.
Database relationships must prevent references to records that do not exist.
5. Values Calculated From Stored Records

The following values should be calculated instead of manually entered:

Total good quantity
Total rejected quantity
Total recorded quantity
Remaining quantity
Completion percentage
Rejection rate
Total downtime
Downtime duration
Active-run count
Completed-run count
Failed-inspection count

Example formulas:

Total recorded quantity = total good quantity + total rejected quantity

Remaining quantity = planned quantity - total good quantity

Completion percentage = total good quantity / planned quantity × 100

Rejection rate = total rejected quantity / total recorded quantity × 100

Downtime duration = downtime end time - downtime start time

Division calculations must safely handle a total of zero.

6. MVP Database Boundary

The following entities are deliberately excluded from the initial database:

Machine
Batch
Defect
DefectCategory
Deviation
CorrectiveAction
InspectionPlan
ProductionArea

These can be introduced after the core production workflow is working, tested and deployed.

7. Open Design Questions

The following decisions must be reviewed before Django models are created:

Can one work order have multiple production runs?
Can an operator have more than one active production run?
How many inspections are required before a run can be completed?
Should production entries be correctable, or should corrections create replacement records?
Should downtime events automatically pause a production run?
Should completion percentage use good quantity or total recorded quantity?
Should supervisors be able to record quantities on behalf of operators?
How should overnight shifts be represented when the end time is earlier than the start time?