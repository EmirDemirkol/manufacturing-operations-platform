# ForgeOps Database Design

## Purpose

This document defines the initial database entities, attributes, relationships and integrity rules for the ForgeOps MVP.

The database uses PostgreSQL.

ForgeOps uses Django's built-in User and Group models for authentication and role management.

All manufacturing examples and demonstration records use synthetic data.

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

### Example

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

### Example

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
- A Production Line cannot be deleted while dependent Production Runs exist.
- A Production Line may be marked inactive instead of being deleted.

### Example

```text
DUB01 / ASSEMBLY / LINE-A01 - Assembly Line A
```

---

## Product

A Product represents a synthetic item manufactured within ForgeOps.

### Attributes

- ID
- Product code
- Product name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Product code must be globally unique.
- Product code may contain uppercase letters, numbers, hyphens and underscores only.
- Product name is required.
- A Product cannot be deleted while dependent Work Orders exist.
- A Product may be marked inactive instead of being deleted.

### Example

```text
PRD-1001 - Synthetic Medical Device Assembly
```

---

## Shift

A Shift represents a scheduled manufacturing working period.

### Attributes

- ID
- Shift name
- Start time
- End time
- Active status
- Created date and time
- Updated date and time

### Rules

- Shift name must be globally unique.
- Start time and end time are required.
- Start time and end time cannot be identical.
- An end time earlier than the start time represents an overnight Shift.
- Overnight Shifts are valid.
- A Shift cannot be deleted while dependent Production Runs exist.
- A Shift may be marked inactive instead of being deleted.

### Example Shifts

```text
Day Shift: 07:00 to 15:00
Evening Shift: 15:00 to 23:00
Night Shift: 23:00 to 07:00
```

---

## WorkOrder

A Work Order represents a planned quantity of a Product that must be manufactured.

### Attributes

- ID
- Work-order number
- Product
- Planned quantity
- Status
- Due date
- Notes
- Active status
- Created date and time
- Updated date and time

### Status Values

- Draft
- Released
- In Progress
- Completed
- Cancelled

### Rules

- Work-order number must be globally unique.
- Work-order numbers may contain uppercase letters, numbers, hyphens and underscores only.
- Planned quantity must be greater than zero.
- Each Work Order relates to exactly one Product.
- One Work Order may contain multiple Production Runs.
- A Work Order may have only one active Production Run at a time.
- A Work Order cannot be deleted while dependent Production Runs exist.
- Product records referenced by Work Orders are protected from deletion.
- A Work Order may be marked inactive instead of being deleted.

### Example

```text
WO-2026-0001
Product: PRD-1001 - Synthetic Medical Device Assembly
Planned Quantity: 1000
Status: Released
```

---

## ProductionRun

A Production Run represents an individual execution of manufacturing work for a Work Order.

### Attributes

- ID
- Work Order
- Production Line
- Shift
- Status
- Started date and time
- Ended date and time
- Good quantity
- Rejected quantity
- Notes
- Active status
- Created date and time
- Updated date and time

### Status Values

- Planned
- Active
- Paused
- Completed
- Cancelled

### Rules

- Each Production Run belongs to exactly one Work Order.
- Each Production Run takes place on exactly one Production Line.
- Each Production Run uses exactly one Shift.
- A Work Order may contain multiple Production Runs.
- A Work Order may have only one Production Run with ACTIVE status at a time.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- An end timestamp cannot occur before its start timestamp.
- Work Orders, Production Lines and Shifts referenced by Production Runs are protected from deletion.
- A Production Run may be marked inactive instead of being deleted.

### Example

```text
Work Order: WO-2026-0001
Production Line: DUB01 / ASSEMBLY / LINE-A01
Shift: Night Shift
Status: Planned
Good Quantity: 0
Rejected Quantity: 0
```

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

A Downtime Reason represents a standard reason for a manufacturing stoppage.

### Attributes

- ID
- Reason code
- Reason name
- Description
- Active status
- Created date and time
- Updated date and time

### Rules

- Reason code must be globally unique.
- Reason code may contain uppercase letters, numbers, hyphens and underscores only.
- Reason name is required.
- A Downtime Reason may be marked inactive instead of being deleted.

### Example Reasons

```text
EQUIPMENT - Equipment fault
MATERIAL - Material shortage
QUALITY - Quality inspection
MAINTENANCE - Planned maintenance
CHANGEOVER - Production changeover
```

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
Downtime duration =
downtime end date and time - downtime start date and time
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

- One Product may have many Work Orders.
- One Work Order belongs to one Product.

## Work-Order Relationships

- One Work Order may have multiple Production Runs.
- One Production Run belongs to one Work Order.
- Only one Production Run for a Work Order may have ACTIVE status at a time.

## Production-Run Relationships

One Production Run belongs to:

- One Work Order
- One Production Line
- One Shift

Future operational models may also associate Users with Production Runs.

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
- Product codes must be globally unique.
- Work-order numbers must be globally unique.
- Downtime Reason codes must be globally unique.
- Business codes may contain uppercase letters, numbers, hyphens and underscores only.
- Shift names must be globally unique.
- Shift start time and end time cannot be identical.
- An end time earlier than a Shift start time represents an overnight Shift.
- Planned Work Order quantities must be greater than zero.
- Production Run good quantities cannot be negative.
- Production Run rejected quantities cannot be negative.
- A Production Run end timestamp cannot occur before its start timestamp.
- Only one Production Run may have ACTIVE status for a Work Order at a time.
- Parent manufacturing records cannot be deleted while dependent child records exist.
- Database relationships must prevent references to records that do not exist.
- Reference and operational records may be marked inactive instead of being deleted.
- Audit records cannot be changed through standard application workflows.
- All manufacturing examples and demonstration records must use synthetic data.

Future workflow rules will include:

- Production Entries can only be added to active Production Runs.
- Open Downtime Events must be closed before Production Run completion.
- Required Quality Inspections must be completed before Production Run completion.
- Inactive reference records should not be selectable for new operational records.

---

# 5. Values Calculated From Stored Records

The following values should be calculated instead of manually entered where the related operational models provide the source data:

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

- Can an Operator have more than one active Production Run?
- How many Quality Inspections are required before a Production Run can be completed?
- Should Production Entries be correctable, or should corrections create replacement records?
- Should Downtime Events automatically pause a Production Run?
- Should completion percentage use good quantity or total recorded quantity?
- Should Supervisors be able to record quantities on behalf of Operators?

The following questions have already been resolved:

- A Work Order may contain multiple Production Runs.
- Only one Production Run for a Work Order may have ACTIVE status at a time.
- Overnight Shifts are represented by an end time earlier than the start time.

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

---

# 9. Operational Reference Models

ForgeOps implements operational reference data used by Work Orders, Production Runs and future Downtime Events.

## Product

A Product represents a synthetic item manufactured within ForgeOps.

### Key Fields

- `code`
- `name`
- `description`
- `is_active`
- `created_at`
- `updated_at`

### Example

```text
PRD-1001 - Synthetic Medical Device Assembly
```

### Rules

- Product codes are globally unique.
- Product codes use uppercase letters, numbers, hyphens and underscores only.
- Product names are required.
- Products may be marked inactive instead of being deleted.
- All Product examples use synthetic data.

## Shift

A Shift represents a scheduled manufacturing working period.

### Key Fields

- `name`
- `start_time`
- `end_time`
- `is_active`
- `created_at`
- `updated_at`

### Examples

```text
Day Shift: 07:00 to 15:00
Evening Shift: 15:00 to 23:00
Night Shift: 23:00 to 07:00
```

### Rules

- Shift names are globally unique.
- Start time and end time are required.
- Start time and end time cannot be identical.
- An end time earlier than the start time represents an overnight Shift.
- Overnight Shifts are valid.
- Shifts may be marked inactive instead of being deleted.

## DowntimeReason

A DowntimeReason represents a standard reason for a manufacturing stoppage.

### Key Fields

- `code`
- `name`
- `description`
- `is_active`
- `created_at`
- `updated_at`

### Examples

```text
EQUIPMENT - Equipment fault
MATERIAL - Material shortage
QUALITY - Quality inspection
MAINTENANCE - Planned maintenance
CHANGEOVER - Production changeover
```

### Rules

- Downtime Reason codes are globally unique.
- Downtime Reason codes use uppercase letters, numbers, hyphens and underscores only.
- Downtime Reason names are required.
- Downtime Reasons may be marked inactive instead of being deleted.
- All DowntimeReason examples use synthetic data.

## Implemented Validation and Administration

- Product and DowntimeReason use the shared business-code validator.
- Product and DowntimeReason codes are protected by database uniqueness constraints.
- Shift names are protected by a database uniqueness constraint.
- Identical Shift start and end times are rejected by model validation.
- Identical Shift start and end times are rejected by a database constraint.
- Overnight Shift detection is available through the `is_overnight` property.
- Product, Shift and DowntimeReason are registered in Django administration.
- Automated tests verify validation, constraints, timestamps, string representations and admin registration.

---

# 10. Work Orders and Production Runs

ForgeOps implements Work Orders and Production Runs to represent planned manufacturing demand and the execution of that manufacturing work.

The operational relationship is:

```text
Product
└── Work Order
    └── Production Run
        ├── Production Line
        └── Shift
```

## WorkOrder

A WorkOrder represents a planned quantity of a Product that must be manufactured.

### Key Fields

- `order_number`
- `product`
- `planned_quantity`
- `status`
- `due_date`
- `notes`
- `is_active`
- `created_at`
- `updated_at`

### Status Values

```text
DRAFT
RELEASED
IN_PROGRESS
COMPLETED
CANCELLED
```

### Example

```text
WO-2026-0001
Product: PRD-1001 - Synthetic Medical Device Assembly
Planned Quantity: 1000
Status: RELEASED
```

### Rules

- Work Order numbers are globally unique.
- Work Order numbers use uppercase letters, numbers, hyphens and underscores only.
- Planned quantity must be greater than zero.
- Each Work Order relates to exactly one Product.
- One Work Order may contain multiple Production Runs.
- Product records referenced by Work Orders are protected from deletion.
- Work Orders may be marked inactive instead of being deleted.
- All Work Order examples use synthetic manufacturing data.

## ProductionRun

A ProductionRun represents an individual execution of manufacturing work for a Work Order.

### Key Fields

- `work_order`
- `production_line`
- `shift`
- `status`
- `started_at`
- `ended_at`
- `good_quantity`
- `rejected_quantity`
- `notes`
- `is_active`
- `created_at`
- `updated_at`

### Status Values

```text
PLANNED
ACTIVE
PAUSED
COMPLETED
CANCELLED
```

### Example

```text
Work Order: WO-2026-0001
Production Line: DUB01 / ASSEMBLY / LINE-A01
Shift: Night Shift
Status: PLANNED
Good Quantity: 0
Rejected Quantity: 0
```

### Rules

- Each Production Run belongs to exactly one Work Order.
- Each Production Run takes place on exactly one Production Line.
- Each Production Run uses exactly one Shift.
- A Work Order may contain multiple Production Runs.
- A Work Order may have only one Production Run with ACTIVE status at a time.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- An end timestamp cannot occur before its start timestamp.
- Work Orders referenced by Production Runs are protected from deletion.
- Production Lines referenced by Production Runs are protected from deletion.
- Shifts referenced by Production Runs are protected from deletion.
- Production Runs may be marked inactive instead of being deleted.
- All Production Run examples use synthetic manufacturing data.

## Implemented Database Constraints

The WorkOrder model includes:

- A database uniqueness constraint for `order_number`.
- A positive-value requirement for `planned_quantity`.
- A database check ensuring `planned_quantity` is greater than zero.
- Protected deletion for referenced Product records.

The ProductionRun model includes:

- A database check ensuring `good_quantity` is non-negative.
- A database check ensuring `rejected_quantity` is non-negative.
- A database constraint preventing `ended_at` from occurring before `started_at`.
- A conditional uniqueness constraint allowing only one ACTIVE Production Run per Work Order.
- Protected deletion for referenced Work Orders.
- Protected deletion for referenced Production Lines.
- Protected deletion for referenced Shifts.

## Implemented Validation and Administration

- Work Order numbers reuse the shared business-code validator.
- Planned Work Order quantities are validated as positive values.
- Production Run quantity fields default to zero.
- Production Run start and end timestamps are validated.
- WorkOrder and ProductionRun are registered in Django administration.
- WorkOrder relationships can be managed through Django administration.
- ProductionRun relationships can be managed through Django administration.
- Django admin uses related-record selection for Products, Production Lines, Shifts and Work Orders.
- Automated tests verify WorkOrder and ProductionRun relationships.
- Automated tests verify model validation.
- Automated tests verify database constraints.
- Automated tests verify deletion protection.
- Automated tests verify status defaults.
- Automated tests verify timestamps.
- Automated tests verify string representations.
- Automated tests verify Django administration registration.
- Automated tests verify that multiple Production Runs may belong to one Work Order.
- Automated tests verify that different Work Orders may each have an active Production Run.
- Automated tests verify that one Work Order cannot have multiple ACTIVE Production Runs simultaneously.

---

# 11. Current Implementation Status

The following database models are currently implemented:

```text
User
Group
Site
ProductionArea
ProductionLine
Product
Shift
DowntimeReason
WorkOrder
ProductionRun
```

The following operational models remain planned for later implementation:

```text
ProductionEntry
DowntimeEvent
QualityInspection
AuditEvent
```

The current implemented operational flow is:

```text
Site
└── ProductionArea
    └── ProductionLine
        └── ProductionRun

Product
└── WorkOrder
    └── ProductionRun

Shift
└── ProductionRun
```

This provides the database foundation required for the next phase of ForgeOps operational development.