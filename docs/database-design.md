# ForgeOps Database Design

## Purpose

This document defines the initial database entities, attributes, relationships and integrity rules for the ForgeOps MVP.

The database uses PostgreSQL.

ForgeOps uses Django's built-in User and Group models for authentication and role management.

---

# 1. Core Entities

## User

Provided by Django's authentication system.

A User represents a person who can log into ForgeOps.

### Important Information

- ID
- Username
- Password hash
- First name
- Last name
- Email
- Active status
- Assigned groups
- Date joined

Django Groups represent the ForgeOps roles:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

---

## Site

A Site represents a fictional manufacturing plant or facility.

### Attributes

- ID
- Code
- Name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Site code must be globally unique.
- Site code may contain uppercase letters, numbers, hyphens and underscores only.
- Site name is required.
- A Site may contain multiple Production Areas.
- A Site cannot be deleted while dependent Production Areas exist.
- A Site may be marked inactive instead of being deleted.

For the MVP, ForgeOps uses one fictional Site, but the structure supports additional Sites later.

Example:

```text
DUB01 - ForgeOps Dublin Plant
```

---

## ProductionArea

A Production Area represents a functional manufacturing area within a Site.

### Attributes

- ID
- Site
- Code
- Name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Each Production Area belongs to exactly one Site.
- A Site may contain multiple Production Areas.
- Production Area code must be unique within its Site.
- The same Production Area code may be reused at another Site.
- Production Area code may contain uppercase letters, numbers, hyphens and underscores only.
- Production Area name is required.
- A Production Area cannot be deleted while dependent Production Lines exist.
- A Production Area may be marked inactive instead of being deleted.

Example:

```text
DUB01 / ASSEMBLY - Final Assembly
```

---

## ProductionLine

A Production Line represents an individual manufacturing line within a Production Area.

### Attributes

- ID
- Production Area
- Code
- Name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Each Production Line belongs to exactly one Production Area.
- A Production Area may contain multiple Production Lines.
- Production Line code must be unique within its Production Area.
- The same Production Line code may be reused in another Production Area.
- Production Line code may contain uppercase letters, numbers, hyphens and underscores only.
- Production Line name is required.
- Inactive Production Lines cannot be selected for new Production Runs.
- A Production Line may be marked inactive instead of being deleted.

Example:

```text
DUB01 / ASSEMBLY / LINE-A01 - Assembly Line A
```

---

## Product

A Product represents a fictional product manufactured at a Site.

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
- Inactive Products cannot be selected for new Work Orders.

---

## Shift

A Shift represents a scheduled working period.

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
- Inactive Shifts cannot be selected for new Production Runs.

Example Shifts:

- Day Shift
- Evening Shift
- Night Shift

---

## WorkOrder

A Work Order represents planned production for a Product.

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
- Each Work Order relates to one Product.
- Cancelled Work Orders cannot be used for new Production Runs.
- The selected Product must be active.

---

## ProductionRun

A Production Run represents the execution of a Work Order on a Production Line during a Shift.

### Attributes

- ID
- Work Order
- Production Line
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

- Each Production Run belongs to one Work Order.
- Each Production Run occurs on one Production Line.
- Each Production Run occurs during one Shift.
- Each Production Run is assigned to one Operator.
- A completed Production Run cannot accept new Production Entries.
- A cancelled Production Run cannot be started.
- The selected Production Line and Shift must be active.

---

## ProductionEntry

A Production Entry represents a quantity recorded during an active Production Run.

### Attributes

- ID
- Production Run
- Good quantity
- Rejected quantity
- Recorded by
- Recorded date and time
- Notes

### Rules

- Each Production Entry belongs to one Production Run.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- At least one quantity must be greater than zero.
- Quantities must be whole numbers.
- Production Entries can only be created for active Production Runs.

### Calculated Values

- Entry total = good quantity + rejected quantity
- Run good total = sum of all good quantities
- Run rejected total = sum of all rejected quantities
- Run total = run good total + run rejected total

Calculated values should normally be derived from Production Entries rather than stored separately.

---

## DowntimeReason

A Downtime Reason represents a standard reason for a production stoppage.

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
- Inactive Downtime Reasons cannot be selected for new Downtime Events.

Example Reasons:

- Equipment fault
- Material shortage
- Quality inspection
- Planned maintenance
- Operator unavailable
- Changeover

---

## DowntimeEvent

A Downtime Event represents a period during which production stopped.

### Attributes

- ID
- Production Run
- Downtime Reason
- Start date and time
- End date and time
- Opened by
- Closed by
- Notes
- Created date and time
- Updated date and time

### Rules

- Each Downtime Event belongs to one Production Run.
- Each Downtime Event has one Downtime Reason.
- Downtime can only be opened for an active Production Run.
- End time cannot be earlier than start time.
- A closed Downtime Event cannot be closed again.
- A Production Run cannot be completed while it has open Downtime.

### Calculated Value

```text
Downtime duration = end date and time - start date and time
```

The duration should be calculated from timestamps rather than manually entered.

---

## QualityInspection

A Quality Inspection represents a basic quality check performed against a Production Run.

### Attributes

- ID
- Production Run
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

- Each Quality Inspection belongs to one Production Run.
- Only authorised Quality users can record the result.
- A completed result must be Passed or Failed.
- Failed results must be visible to authorised Supervisors and Managers.
- Required Quality Inspections must be completed before the Production Run is completed.

---

## AuditEvent

An Audit Event represents an important action performed in ForgeOps.

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

- Audit Events are created automatically.
- Audit Events cannot be edited through the normal application interface.
- Audit Events cannot be deleted through the normal application interface.
- An Audit Event may reference a record without using a direct database relationship to every possible entity.

---

# 2. Relationships

## Site Relationships

- One Site has many Production Areas.
- One Production Area belongs to one Site.

## Production Area Relationships

- One Production Area has many Production Lines.
- One Production Line belongs to one Production Area.

## Product Relationships

- One Product has many Work Orders.
- One Work Order belongs to one Product.

## Work-Order Relationships

- One Work Order may have one or more Production Runs.
- One Production Run belongs to one Work Order.

The MVP will normally use one Production Run per Work Order, but the database should not unnecessarily prevent future split runs.

## Production-Run Relationships

One Production Run belongs to:

- One Work Order
- One Production Line
- One Shift
- One assigned User

One Production Run can have many:

- Production Entries
- Downtime Events
- Quality Inspections

## Production-Entry Relationships

- One Production Run has many Production Entries.
- One Production Entry belongs to one Production Run.
- One User may record many Production Entries.

## Downtime Relationships

- One Downtime Reason may be used by many Downtime Events.
- One Production Run may have many Downtime Events.
- One Downtime Event belongs to one Production Run.
- One Downtime Event uses one Downtime Reason.

## Quality Relationships

- One Production Run may have many Quality Inspections.
- One Quality Inspection belongs to one Production Run.
- One Quality User may complete many Quality Inspections.

## Audit Relationships

- One User may generate many Audit Events.
- Each Audit Event records one action performed by one User.
- Audit Events identify affected records using record type and record identifier.

---

# 3. Relationship Summary

```text
Site
└── ProductionArea
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
```

---

# 4. Initial Integrity Rules

- Site codes must be globally unique.
- Production Area codes must be unique within each Site.
- Production Line codes must be unique within each Production Area.
- Product codes must be unique.
- Work-order numbers must be unique.
- Downtime-reason codes must be unique.
- Business codes may contain uppercase letters, numbers, hyphens and underscores only.
- Planned quantities must be greater than zero.
- Good and rejected quantities cannot be negative.
- Production Entries can only be added to active Production Runs.
- Downtime end times cannot occur before downtime start times.
- Completed Production Runs cannot accept new operational records.
- Open Downtime Events must be closed before Production Run completion.
- Required Quality Inspections must be completed before Production Run completion.
- Inactive reference records cannot be selected for new operational records.
- Parent manufacturing records cannot be deleted while dependent child records exist.
- Audit records cannot be changed through standard application workflows.
- Database relationships must prevent references to records that do not exist.
- All manufacturing examples and demonstration records must use synthetic data.

---

# 5. Values Calculated From Stored Records

The following values should be calculated instead of manually entered:

- Total good quantity
- Total rejected quantity
- Total recorded quantity
- Remaining quantity
- Completion percentage
- Rejection rate
- Total downtime
- Downtime duration
- Active-run count
- Completed-run count
- Failed-inspection count

Example formulas:

```text
Total recorded quantity =
total good quantity + total rejected quantity
```

```text
Remaining quantity =
planned quantity - total good quantity
```

```text
Completion percentage =
total good quantity / planned quantity × 100
```

```text
Rejection rate =
total rejected quantity / total recorded quantity × 100
```

```text
Downtime duration =
downtime end time - downtime start time
```

Division calculations must safely handle a total of zero.

---

# 6. MVP Database Boundary

The following entities are deliberately excluded from the initial database:

- Machine
- Batch
- Defect
- DefectCategory
- Deviation
- CorrectiveAction
- InspectionPlan

These entities can be introduced after the core production workflow is working, tested and deployed.

---

# 7. Open Design Questions

The following decisions must be reviewed before the related operational models are implemented:

- Can one Work Order have multiple Production Runs?
- Can an Operator have more than one active Production Run?
- How many Quality Inspections are required before a Production Run can be completed?
- Should Production Entries be correctable, or should corrections create replacement records?
- Should Downtime Events automatically pause a Production Run?
- Should completion percentage use good quantity or total recorded quantity?
- Should Supervisors be able to record quantities on behalf of Operators?
- How should overnight Shifts be represented when the end time is earlier than the start time?

---

# 8. Implemented Manufacturing Hierarchy

ForgeOps currently implements the following physical manufacturing hierarchy:

```text
Site
└── Production Area
    └── Production Line
```

## Implemented Data Integrity Rules

- Site codes are globally unique.
- Production Area codes are unique within each Site.
- Production Line codes are unique within each Production Area.
- Business codes contain uppercase letters, numbers, hyphens and underscores only.
- Parent records cannot be deleted while dependent child records exist.
- Records may be marked inactive instead of being deleted.
- Created and updated timestamps are recorded automatically.
- The hierarchy can be managed through Django administration.
- Automated tests verify relationships, constraints, validation and deletion protection.
- All manufacturing examples use synthetic data.