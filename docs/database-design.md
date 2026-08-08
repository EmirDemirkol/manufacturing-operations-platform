# ForgeOps Database Design

## Purpose

This document defines the database entities, attributes, relationships and integrity rules for the ForgeOps manufacturing operations platform.

ForgeOps currently uses SQLite for local development through the Django ORM.

PostgreSQL is the intended database architecture for a later deployment phase.

ForgeOps uses Django's built-in User and Group models for authentication and role management.

All manufacturing examples, manual demonstrations and automated test records use synthetic data.

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

Users are also referenced by transactional records for operational traceability.

Current examples include:

- `ProductionEntry.recorded_by`
- `DowntimeEvent.opened_by`
- `DowntimeEvent.closed_by`

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

```text
DRAFT
RELEASED
IN_PROGRESS
COMPLETED
CANCELLED
```

### Rules

- Work-order number must be globally unique.
- Work-order numbers may contain uppercase letters, numbers, hyphens and underscores only.
- Planned quantity must be greater than zero.
- Each Work Order relates to exactly one Product.
- One Work Order may contain multiple Production Runs.
- A Work Order may have only one ACTIVE Production Run at a time.
- A Work Order cannot be deleted while dependent Production Runs exist.
- Product records referenced by Work Orders are protected from deletion.
- A Work Order may be marked inactive instead of being deleted.

### Example

```text
WO-2026-0001
Product: PRD-1001 - Synthetic Medical Device Assembly
Planned Quantity: 1000
Status: RELEASED
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
- Notes
- Active status
- Created date and time
- Updated date and time

Production quantities are not stored directly on ProductionRun.

Instead, good and rejected quantities are derived from related ProductionEntry records.

### Derived Values

- Good quantity
- Rejected quantity
- Total recorded quantity

Remaining quantity and completion percentage remain unresolved business definitions for a later workflow issue and must not be treated as final business rules yet.

### Status Values

```text
PLANNED
ACTIVE
PAUSED
COMPLETED
CANCELLED
```

### Rules

- Each Production Run belongs to exactly one Work Order.
- Each Production Run takes place on exactly one Production Line.
- Each Production Run uses exactly one Shift.
- A Work Order may contain multiple Production Runs.
- A Work Order may have only one Production Run with ACTIVE status at a time.
- An end timestamp cannot occur before its start timestamp.
- Work Orders referenced by Production Runs are protected from deletion.
- Production Lines referenced by Production Runs are protected from deletion.
- Shifts referenced by Production Runs are protected from deletion.
- A Production Run cannot be deleted while dependent Production Entries exist.
- A Production Run cannot be deleted while dependent Downtime Events exist.
- A Production Run may be marked inactive instead of being deleted.

### Example

```text
Work Order: WO-2026-0001
Production Line: DUB01 / ASSEMBLY / LINE-A01
Shift: Night Shift
Status: ACTIVE
Good Quantity: derived from ProductionEntry records
Rejected Quantity: derived from ProductionEntry records
```

---

## ProductionEntry

A Production Entry represents an individual manufacturing quantity recording made against an ACTIVE Production Run.

ProductionEntry provides an incremental record of manufacturing output rather than repeatedly overwriting quantity counters on ProductionRun.

### Attributes

- ID
- Production Run
- Good quantity
- Rejected quantity
- Recorded by
- Recorded date and time
- Notes

### Rules

- Each Production Entry belongs to exactly one Production Run.
- Each Production Entry is recorded by exactly one Django User.
- One Production Run may contain multiple Production Entries.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- Production quantities must be whole numbers.
- At least one of good quantity or rejected quantity must be greater than zero.
- A good-only Production Entry is valid.
- A rejected-only Production Entry is valid.
- A Production Entry containing both good and rejected quantities is valid.
- A Production Entry containing zero good and zero rejected quantity is invalid.
- Production Entries may only be recorded against Production Runs with ACTIVE status.
- PLANNED Production Runs cannot accept Production Entries.
- PAUSED Production Runs cannot accept Production Entries.
- COMPLETED Production Runs cannot accept Production Entries.
- CANCELLED Production Runs cannot accept Production Entries.
- A Production Run referenced by a Production Entry is protected from deletion.
- A User referenced by a Production Entry is protected from deletion.
- The recorded timestamp is created automatically.

### Example

```text
Production Run: WO-2026-0001 / LINE-A01
Good Quantity: 250
Rejected Quantity: 5
Recorded By: synthetic_operator
Recorded At: automatically generated
```

### Calculated Values

```text
Entry total =
good quantity + rejected quantity
```

```text
Run good total =
sum of all ProductionEntry good quantities
```

```text
Run rejected total =
sum of all ProductionEntry rejected quantities
```

```text
Run total =
run good total + run rejected total
```

ProductionRun quantity totals must be derived from ProductionEntry records rather than maintained as duplicate stored values.

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
- A Downtime Reason referenced by a DowntimeEvent is protected from deletion.

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

A Downtime Event represents one period of production downtime recorded against a ProductionRun.

DowntimeEvent was implemented as part of FO-008.

### Attributes

- ID
- Production Run
- Downtime Reason
- Started date and time
- Ended date and time
- Opened by
- Closed by
- Notes
- Created date and time
- Updated date and time

### Relationships

```text
DowntimeEvent.production_run -> ProductionRun
DowntimeEvent.downtime_reason -> DowntimeReason
DowntimeEvent.opened_by -> User
DowntimeEvent.closed_by -> User
```

The relationships use protected deletion to preserve operational history.

### Rules

- Each Downtime Event belongs to exactly one Production Run.
- Each Downtime Event uses exactly one Downtime Reason.
- A Downtime Event may only be opened against a Production Run with ACTIVE status.
- PLANNED Production Runs cannot accept new Downtime Events.
- PAUSED Production Runs cannot accept new Downtime Events.
- COMPLETED Production Runs cannot accept new Downtime Events.
- CANCELLED Production Runs cannot accept new Downtime Events.
- `started_at` is required.
- `ended_at` may remain empty while downtime is open.
- `ended_at` cannot occur before `started_at`.
- An open Downtime Event has no `ended_at`.
- An open Downtime Event has no `closed_by` User.
- A closed Downtime Event has an `ended_at` value.
- A closed Downtime Event records a `closed_by` User.
- Only one open Downtime Event may exist for a Production Run at one time.
- One Production Run may contain multiple closed Downtime Events over time.
- `opened_by` is required.
- `closed_by` is optional while downtime remains open.
- Notes are optional.
- ProductionRun records referenced by Downtime Events are protected from deletion.
- DowntimeReason records referenced by Downtime Events are protected from deletion.
- Users referenced through `opened_by` are protected from deletion.
- Users referenced through `closed_by` are protected from deletion.
- Automatic ProductionRun pause and resume behaviour is not implemented by FO-008.
- FO-008 does not define closed Downtime Events as immutable records.
- FO-008 does not implement ProductionRun completion blocking based on open downtime.

### Open Event Example

```text
Production Run: WO-2026-0001 / LINE-A01
Downtime Reason: EQUIPMENT - Equipment fault
Started At: 2026-08-08 12:48
Ended At: blank
Opened By: admin
Closed By: blank
State: Open
Duration: Open
```

### Closed Event Example

```text
Production Run: WO-2026-0001 / LINE-A01
Downtime Reason: EQUIPMENT - Equipment fault
Started At: 2026-08-08 12:48
Ended At: 2026-08-08 12:53
Opened By: admin
Closed By: admin
State: Closed
Duration: derived from timestamps
```

All examples are synthetic.

### Derived Duration

Downtime duration is not stored independently.

For a closed event:

```text
Downtime duration =
ended_at - started_at
```

For an open event:

```text
duration = None
```

The Django administration displays an open event as `Open` until an end timestamp exists.

### Database Constraints

DowntimeEvent currently includes:

```text
downtime_event_end_not_before_start
```

This prevents an end timestamp from occurring before the start timestamp.

It also includes:

```text
downtime_event_close_state_consistent
```

This keeps `ended_at` and `closed_by` consistent between open and closed states.

It also includes:

```text
unique_open_downtime_per_production_run
```

This prevents more than one open Downtime Event from existing for the same ProductionRun at one time.

### Django Administration

DowntimeEvent is registered in Django administration.

The current administration view supports inspection of:

- Production Run
- Downtime Reason
- Open or closed state
- Started timestamp
- Ended timestamp
- Derived duration
- Opening User
- Closing User

The administration configuration also provides filters, search fields, autocomplete fields and related-object query optimisation.

### Manual FO-008 Verification

FO-008 was manually exercised using synthetic records through Django administration.

The manual verification demonstrated that:

1. A ProductionRun can be moved into ACTIVE status.
2. A DowntimeEvent can be opened against that ACTIVE ProductionRun.
3. The open event records its DowntimeReason and opening User.
4. `ended_at` and `closed_by` remain empty while the event is open.
5. A second open DowntimeEvent for the same ProductionRun is rejected.
6. The original DowntimeEvent can be closed by supplying `ended_at` and `closed_by`.
7. The event then displays as Closed.
8. The duration is calculated from the stored timestamps.

All records used for this verification were synthetic.

---

## Planned QualityInspection

This model is part of the planned ForgeOps architecture and has not yet been implemented.

A Quality Inspection represents a basic quality check performed against a Production Run.

### Planned Attributes

- ID
- Production Run
- Result
- Notes
- Completed by
- Completed date and time
- Created date and time
- Updated date and time

### Planned Result Values

```text
PENDING
PASSED
FAILED
```

### Planned Rules

- Each Quality Inspection belongs to one Production Run.
- Quality actions should be role restricted.
- A completed result should be PASSED or FAILED.
- Failed results should be visible to authorised Supervisors and Managers.
- Required Quality Inspections may need to be completed before Production Run completion.

The exact QualityInspection implementation must be decided by its future GitHub issue.

---

## Planned AuditEvent

This model is part of the planned ForgeOps architecture and has not yet been implemented.

An Audit Event represents an important action performed in ForgeOps.

### Planned Attributes

- ID
- User
- Action type
- Record type
- Record identifier
- Description
- Event date and time

### Example Planned Action Types

```text
Created
Updated
Assigned
Started
Completed
Cancelled
Opened
Closed
Corrected
```

### Planned Principles

- Audit Events should be created automatically.
- Audit Events should not be editable through normal application workflows.
- Audit Events should not be deletable through normal application workflows.
- An Audit Event may identify an affected record using record type and record identifier rather than requiring a direct foreign key to every possible model.

ForgeOps audit history is an educational traceability feature and must not be represented as a validated regulatory audit trail.

The exact AuditEvent implementation must be decided by its future GitHub issue.

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

- one Work Order
- one Production Line
- one Shift

One Production Run can currently have many:

- Production Entries
- Downtime Events

A future Production Run may also have:

- Quality Inspections

## Production-Entry Relationships

- One Production Run may have many Production Entries.
- One Production Entry belongs to exactly one Production Run.
- One User may record many Production Entries.
- One Production Entry is recorded by exactly one User.
- Production Entries are available through the ProductionRun `production_entries` relationship.
- User production entries are available through the User `production_entries` relationship.

## Downtime Relationships

- One Production Run may have many Downtime Events over time.
- One Downtime Event belongs to exactly one Production Run.
- One Downtime Reason may be used by many Downtime Events.
- One Downtime Event uses exactly one Downtime Reason.
- One User may open many Downtime Events.
- One User may close many Downtime Events.
- ProductionRun downtime records are available through `downtime_events`.
- DowntimeReason downtime records are available through `downtime_events`.
- Opening User relationships are available through `opened_downtime_events`.
- Closing User relationships are available through `closed_downtime_events`.

## Planned Quality Relationships

- One Production Run may have many Quality Inspections.
- One Quality Inspection belongs to one Production Run.
- One Quality User may complete many Quality Inspections.

## Planned Audit Relationships

- One User may generate many Audit Events.
- Each Audit Event may record one action performed by one User.
- Audit Events may identify affected records using record type and record identifier.

---

# 3. Current Relationship Summary

```text
Site
└── ProductionArea
    └── ProductionLine
        └── ProductionRun
            ├── ProductionEntry
            └── DowntimeEvent
                └── DowntimeReason

Product
└── WorkOrder
    └── ProductionRun

Shift
└── ProductionRun

User
├── ProductionEntry
├── DowntimeEvent.opened_by
└── DowntimeEvent.closed_by
```

Planned future relationships include QualityInspection and AuditEvent.

---

# 4. Current Integrity Rules

## Manufacturing Hierarchy

- Site codes must be globally unique.
- Production Area codes must be unique within each Site.
- Production Line codes must be unique within each Production Area.
- Business codes may contain uppercase letters, numbers, hyphens and underscores only.

## Product

- Product codes must be globally unique.
- Products referenced by Work Orders cannot be deleted.

## Shift

- Shift names must be globally unique.
- Shift start time and end time cannot be identical.
- An end time earlier than a Shift start time represents an overnight Shift.
- Overnight Shifts are valid.
- Shifts referenced by Production Runs cannot be deleted.

## DowntimeReason

- Downtime Reason codes must be globally unique.
- Downtime Reason codes use the shared business-code format.
- Downtime Reasons referenced by Downtime Events cannot be deleted.

## WorkOrder

- Work-order numbers must be globally unique.
- Planned quantities must be greater than zero.
- Products referenced by Work Orders are protected from deletion.
- Work Orders referenced by Production Runs are protected from deletion.

## ProductionRun

- A Production Run end timestamp cannot occur before its start timestamp.
- Only one Production Run may have ACTIVE status for a Work Order at a time.
- Different Work Orders may each have an ACTIVE Production Run.
- Production Lines referenced by Production Runs are protected from deletion.
- Shifts referenced by Production Runs are protected from deletion.
- ProductionRun quantities are derived from ProductionEntry records rather than stored as duplicate counters.
- Production Runs referenced by Production Entries cannot be deleted.
- Production Runs referenced by Downtime Events cannot be deleted.

## ProductionEntry

- Good quantities cannot be negative.
- Rejected quantities cannot be negative.
- A ProductionEntry must contain at least one recorded unit.
- Zero good and zero rejected together are invalid.
- Production Entries may only be added to ACTIVE Production Runs.
- Production Runs referenced by Production Entries cannot be deleted.
- Users referenced by Production Entries cannot be deleted.
- Recorded timestamps are generated automatically.

## DowntimeEvent

- Downtime Events may only be opened against ACTIVE Production Runs.
- End timestamps cannot occur before start timestamps.
- An open event has no `ended_at`.
- An open event has no `closed_by`.
- A closed event has both `ended_at` and `closed_by`.
- Only one open Downtime Event may exist for one Production Run at a time.
- Multiple closed Downtime Events may exist for the same Production Run.
- ProductionRun references use protected deletion.
- DowntimeReason references use protected deletion.
- Opening User references use protected deletion.
- Closing User references use protected deletion.
- Duration is derived from timestamps.

## General Integrity

- Database relationships must prevent references to records that do not exist.
- Parent manufacturing records cannot be deleted while protected dependent records exist.
- Reference and operational records supporting inactive status may be marked inactive instead of being deleted.
- All manufacturing examples, manual demonstrations and automated tests must use synthetic data.

---

# 5. Values Calculated From Stored Records

The following values should be calculated instead of manually entered where the related operational models provide the source data:

- total good quantity
- total rejected quantity
- total recorded quantity
- remaining quantity
- completion percentage
- rejection rate
- total downtime
- downtime duration
- active-run count
- completed-run count
- failed-inspection count

ProductionRun manufacturing totals are derived directly from related ProductionEntry records.

## Total Good Quantity

```text
Total good quantity =
sum of ProductionEntry good quantities
```

## Total Rejected Quantity

```text
Total rejected quantity =
sum of ProductionEntry rejected quantities
```

## Total Recorded Quantity

```text
Total recorded quantity =
total good quantity + total rejected quantity
```

## Remaining Quantity

The final business definition of remaining quantity remains unresolved.

It must not be treated as a final business rule until the relevant operational workflow issue explicitly resolves how production progress should be measured.

## Completion Percentage

The final business definition of completion percentage remains unresolved.

Possible approaches include:

```text
good quantity / planned quantity × 100
```

or:

```text
total recorded quantity / planned quantity × 100
```

The final calculation must be decided explicitly during the relevant operational or analytics workflow issue.

## Rejection Rate

A possible rejection-rate calculation is:

```text
rejected quantity / total recorded quantity × 100
```

Any implementation must safely handle a total recorded quantity of zero.

## Downtime Duration

For a closed DowntimeEvent:

```text
downtime duration =
ended_at - started_at
```

Open Downtime Events have no completed duration.

## Total Downtime

A future operational metric may calculate:

```text
total downtime =
sum of closed DowntimeEvent durations
```

The reporting implementation is not part of FO-008.

---

# 6. MVP Database Boundary

The following entities are deliberately excluded from the initial ForgeOps MVP:

- Machine
- Batch
- Defect
- DefectCategory
- Deviation
- CorrectiveAction
- InspectionPlan

These entities should not be introduced until the core production workflow is working and the roadmap deliberately expands to include them.

---

# 7. Open Design Questions

The following decisions remain unresolved:

- Can an Operator have more than one ACTIVE Production Run?
- How many Quality Inspections are required before a Production Run can be completed?
- Should Production Entries be correctable, or should corrections create replacement records?
- Should Downtime Events automatically pause a Production Run?
- Should closing downtime automatically resume a Production Run?
- Should open Downtime Events block Production Run completion?
- Should closed Downtime Events become immutable after closure?
- Should completion percentage use good quantity or total recorded quantity?
- How should remaining quantity be calculated?
- Should Supervisors be able to record quantities on behalf of Operators?

These decisions should be made only when their related workflow or model issue is implemented.

The following decisions have already been resolved:

- A Work Order may contain multiple Production Runs.
- Only one Production Run for a Work Order may have ACTIVE status at a time.
- Overnight Shifts are represented by an end time earlier than the start time.
- Production quantities are recorded as individual ProductionEntry records.
- ProductionRun good and rejected totals are derived from ProductionEntry records.
- Production Entries may only be recorded against ACTIVE Production Runs.
- Production Entries record the User responsible for the entry.
- Production Entry timestamps are generated automatically.
- Downtime Events are recorded as individual transactional records.
- Downtime Events may only be opened against ACTIVE Production Runs.
- Only one open Downtime Event may exist for a Production Run at one time.
- Downtime duration is derived from start and end timestamps.
- Downtime opening and closing Users are traceable.
- FO-008 does not automatically pause or resume Production Runs.

---

# 8. Implemented Manufacturing Hierarchy

ForgeOps currently implements the following physical manufacturing hierarchy:

```text
Site
└── ProductionArea
    └── ProductionLine
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

ForgeOps implements operational reference data used by Work Orders, Production Runs and Downtime Events.

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
- Downtime Reasons referenced by Downtime Events are protected from deletion.
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

ForgeOps implements WorkOrder and ProductionRun to represent planned manufacturing demand and execution.

The current operational relationship is:

```text
Product
└── WorkOrder
    └── ProductionRun
        ├── ProductionEntry
        ├── DowntimeEvent
        ├── ProductionLine
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
- `notes`
- `is_active`
- `created_at`
- `updated_at`

### Derived Properties

- `good_quantity`
- `rejected_quantity`

These totals are calculated from related ProductionEntry records.

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
Status: ACTIVE
Good Quantity: derived from ProductionEntry records
Rejected Quantity: derived from ProductionEntry records
```

### Rules

- Each Production Run belongs to exactly one Work Order.
- Each Production Run takes place on exactly one Production Line.
- Each Production Run uses exactly one Shift.
- A Work Order may contain multiple Production Runs.
- A Work Order may have only one Production Run with ACTIVE status at a time.
- An end timestamp cannot occur before its start timestamp.
- Work Orders referenced by Production Runs are protected from deletion.
- Production Lines referenced by Production Runs are protected from deletion.
- Shifts referenced by Production Runs are protected from deletion.
- Production Runs referenced by Production Entries are protected from deletion.
- Production Runs referenced by Downtime Events are protected from deletion.
- Production Runs may be marked inactive instead of being deleted.
- All Production Run examples use synthetic manufacturing data.

## Implemented Database Constraints

The WorkOrder model includes:

- globally unique `order_number`
- positive `planned_quantity`
- database check requiring `planned_quantity > 0`
- protected Product relationship

The ProductionRun model includes:

- database protection against `ended_at < started_at`
- conditional uniqueness allowing only one ACTIVE Production Run per Work Order
- protected WorkOrder relationship
- protected ProductionLine relationship
- protected Shift relationship

Production quantities are not duplicated in ProductionRun database fields.

## Implemented Validation and Administration

- Work Order numbers reuse the shared business-code validator.
- Planned Work Order quantities are validated as positive values.
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
- Automated tests verify that different Work Orders may each have an ACTIVE Production Run.
- Automated tests verify that one Work Order cannot have multiple ACTIVE Production Runs simultaneously.
- Automated tests verify that ProductionRun quantity totals default to zero when no Production Entries exist.

---

# 11. Production Entries

ForgeOps implements ProductionEntry to provide traceable, incremental manufacturing quantity recording.

Before ProductionEntry was introduced, good and rejected quantities were stored directly on ProductionRun.

The implemented design replaces those stored counters with individual ProductionEntry records.

The architecture is:

```text
ProductionRun
└── ProductionEntry
    ├── good_quantity
    ├── rejected_quantity
    ├── recorded_by
    ├── recorded_at
    └── notes
```

A Production Run can therefore contain a history such as:

```text
Production Run: WO-2026-0001 / LINE-A01

Entry 1
Good: 300
Rejected: 4

Entry 2
Good: 250
Rejected: 3

Entry 3
Good: 425
Rejected: 18
```

The resulting ProductionRun totals are:

```text
Good Quantity: 975
Rejected Quantity: 25
Total Recorded Quantity: 1000
```

The ProductionRun does not store `975` and `25` independently.

Instead, ForgeOps derives those values from the ProductionEntry history.

## ProductionEntry Key Fields

- `production_run`
- `recorded_by`
- `good_quantity`
- `rejected_quantity`
- `recorded_at`
- `notes`

## Relationships

- Each ProductionEntry belongs to exactly one ProductionRun.
- Each ProductionEntry is recorded by exactly one User.
- One ProductionRun may contain multiple ProductionEntry records.
- One User may record multiple ProductionEntry records.
- Related entries can be accessed from a ProductionRun through `production_entries`.
- Related entries can be accessed from a User through `production_entries`.

## Quantity Validation

- `good_quantity` defaults to zero.
- `rejected_quantity` defaults to zero.
- Good quantity cannot be negative.
- Rejected quantity cannot be negative.
- At least one quantity must be greater than zero.
- A good-only entry is valid.
- A rejected-only entry is valid.
- An entry containing both quantities is valid.
- An entry containing zero good and zero rejected quantity is invalid.

These rules are enforced through model validation and database constraints.

## Production Run Status Validation

Production Entries may only be recorded against Production Runs with:

```text
ACTIVE
```

Entries are rejected for Production Runs with:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

## Production Totals

ProductionRun exposes derived totals calculated from related ProductionEntry records.

```text
ProductionRun.good_quantity =
sum of related ProductionEntry.good_quantity values
```

```text
ProductionRun.rejected_quantity =
sum of related ProductionEntry.rejected_quantity values
```

If a ProductionRun has no ProductionEntry records:

```text
good_quantity = 0
rejected_quantity = 0
```

## Traceability

Each ProductionEntry records:

- the ProductionRun receiving the quantity
- the User responsible for recording the quantity
- good quantity
- rejected quantity
- recorded timestamp
- optional notes

The `recorded_at` timestamp is generated automatically.

## Deletion Protection

- A ProductionRun cannot be deleted while ProductionEntry records reference it.
- A User cannot be deleted while ProductionEntry records reference that User as `recorded_by`.

## Django Administration

ProductionEntry is registered in Django administration.

Administrative users can inspect ProductionEntry records together with related operational information.

The administration label uses the correct plural:

```text
Production entries
```

## Implemented Migration

The ProductionEntry architecture is introduced through:

```text
0005_create_production_entries
```

The migration:

- creates ProductionEntry
- links ProductionEntry to ProductionRun
- links ProductionEntry to Django User
- adds the automatically generated `recorded_at` timestamp
- removes stored `good_quantity` from ProductionRun
- removes stored `rejected_quantity` from ProductionRun
- removes the old ProductionRun quantity constraints
- adds non-negative quantity constraints to ProductionEntry
- adds a database constraint requiring at least one recorded unit

## Automated Validation

Automated tests verify:

- ProductionEntry relationships
- default quantity values
- automatic timestamp creation
- good-only Production Entries
- rejected-only Production Entries
- combined good and rejected Production Entries
- rejection of negative good quantities
- rejection of negative rejected quantities
- rejection of zero-good and zero-rejected entries
- multiple Production Entries for one ProductionRun
- acceptance of entries for ACTIVE Production Runs
- rejection of entries for PLANNED Production Runs
- rejection of entries for PAUSED Production Runs
- rejection of entries for COMPLETED Production Runs
- rejection of entries for CANCELLED Production Runs
- ProductionRun totals derived from Production Entries
- ProductionRun totals defaulting to zero without entries
- ProductionRun deletion protection
- User deletion protection
- ProductionEntry string representation
- ProductionEntry Django administration registration

All ProductionEntry examples and test records use synthetic manufacturing data.

---

# 12. Downtime Events

FO-008 implements DowntimeEvent as the transactional model for production stoppages.

The architecture is:

```text
ProductionRun
└── DowntimeEvent
    ├── downtime_reason
    ├── started_at
    ├── ended_at
    ├── opened_by
    ├── closed_by
    └── notes
```

## DowntimeEvent Key Fields

- `production_run`
- `downtime_reason`
- `started_at`
- `ended_at`
- `opened_by`
- `closed_by`
- `notes`
- `created_at`
- `updated_at`

## Relationships

- Each DowntimeEvent belongs to exactly one ProductionRun.
- Each DowntimeEvent uses exactly one DowntimeReason.
- Each DowntimeEvent records exactly one opening User.
- A closed DowntimeEvent records a closing User.
- One ProductionRun may contain multiple DowntimeEvents over time.
- One DowntimeReason may be referenced by multiple DowntimeEvents.
- One User may open multiple DowntimeEvents.
- One User may close multiple DowntimeEvents.

Reverse relationships use:

```text
ProductionRun.downtime_events
DowntimeReason.downtime_events
User.opened_downtime_events
User.closed_downtime_events
```

## Production Run Status Validation

A new DowntimeEvent may only be opened against:

```text
ACTIVE
```

New downtime is rejected for:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

The ACTIVE requirement applies when the DowntimeEvent is created.

FO-008 does not automatically modify ProductionRun status when downtime opens or closes.

## Open and Closed States

An open DowntimeEvent has:

```text
ended_at = null
closed_by = null
```

A closed DowntimeEvent has:

```text
ended_at = populated
closed_by = populated
```

The database protects the consistency of those states.

## Timestamp Validation

A closed DowntimeEvent must satisfy:

```text
ended_at >= started_at
```

Invalid timestamp ordering is rejected through model validation and a database constraint.

## One Open Downtime Event Per Run

Only one DowntimeEvent with no end timestamp may exist for a ProductionRun at one time.

Conceptually:

```text
one ProductionRun
    -> maximum one open DowntimeEvent
```

A ProductionRun may still have multiple historical closed DowntimeEvents.

## Duration

Duration is derived rather than stored.

```text
duration =
ended_at - started_at
```

An open DowntimeEvent returns no completed duration.

## Traceability

DowntimeEvent preserves:

- which ProductionRun stopped
- why it stopped
- when downtime started
- when downtime ended
- who opened downtime
- who closed downtime
- optional notes

## Deletion Protection

The following relationships use protected deletion:

- ProductionRun
- DowntimeReason
- opening User
- closing User

This prevents deletion of referenced records from destroying downtime history.

## Django Administration

DowntimeEvent is registered in Django administration.

The current administrative list displays:

- Production Run
- Downtime Reason
- state
- started timestamp
- ended timestamp
- derived duration
- opened by
- closed by

Search, filtering, autocomplete and related-object optimisation are configured for practical inspection.

## Manual Synthetic Verification

FO-008 was manually tested through Django administration using synthetic data.

The test flow demonstrated:

```text
ProductionRun -> ACTIVE

DowntimeEvent -> Open
Reason -> EQUIPMENT
Opened by -> admin
Ended at -> blank
Closed by -> blank
```

A second open DowntimeEvent for the same ProductionRun was rejected by:

```text
unique_open_downtime_per_production_run
```

The original event was then closed by adding:

```text
ended_at
closed_by
```

The administration page correctly displayed:

```text
State: Closed
Duration: derived from timestamps
Closed by: admin
```

## Implemented Migration

DowntimeEvent is introduced through:

```text
0006_downtimeevent
```

The migration:

- creates DowntimeEvent
- links DowntimeEvent to ProductionRun
- links DowntimeEvent to DowntimeReason
- links `opened_by` to Django User
- links optional `closed_by` to Django User
- adds `started_at`
- adds optional `ended_at`
- adds optional notes
- adds creation and update timestamps
- adds the end-not-before-start constraint
- adds the open/closed state consistency constraint
- adds the one-open-event-per-ProductionRun constraint

The migration depends on:

```text
0005_create_production_entries
```

and Django's swappable User model dependency.

## Automated Validation

FO-008 automated tests verify:

- expected DowntimeEvent relationships
- open-event defaults
- creation against ACTIVE ProductionRuns
- rejection against PLANNED ProductionRuns
- rejection against PAUSED ProductionRuns
- rejection against COMPLETED ProductionRuns
- rejection against CANCELLED ProductionRuns
- model validation for invalid timestamp ordering
- database rejection of invalid timestamp ordering
- prevention of multiple open DowntimeEvents for one ProductionRun
- multiple closed DowntimeEvents for one ProductionRun
- open-event `closed_by` consistency
- closed-event `closed_by` consistency
- database close-state consistency
- derived closed-event duration
- ProductionRun deletion protection
- DowntimeReason deletion protection
- opening User deletion protection
- closing User deletion protection
- readable string representation
- Django admin registration

All FO-008 tests use synthetic manufacturing data.

---

# 13. Migration History

The current ForgeOps core migration sequence is:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
```

All six migrations are currently applied in the local SQLite development database.

---

# 14. Current Test Milestone

The current full core test milestone is:

```text
Ran 98 tests
OK
```

Historical milestones include:

```text
FO-005: 34 tests
FO-006: 58 tests
FO-007: 77 tests
FO-008: 98 tests
```

FO-008 adds DowntimeEvent coverage without replacing or removing the existing FO-007 test baseline.

---

# 15. Current Implementation Status

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
ProductionEntry
DowntimeEvent
```

The current implemented operational structure is:

```text
Site
└── ProductionArea
    └── ProductionLine
        └── ProductionRun
            ├── ProductionEntry
            └── DowntimeEvent

Product
└── WorkOrder
    └── ProductionRun

Shift
└── ProductionRun

DowntimeReason
└── DowntimeEvent

User
├── ProductionEntry
├── DowntimeEvent.opened_by
└── DowntimeEvent.closed_by
```

The following operational models remain planned:

```text
QualityInspection
AuditEvent
```

The current database foundation supports:

- authenticated ForgeOps users
- role-based user groups
- manufacturing Sites
- Production Areas
- Production Lines
- Product reference data
- manufacturing Shifts
- Downtime Reason reference data
- Work Order planning
- Production Run execution
- incremental Production Entry recording
- derived ProductionRun quantity totals
- transactional Downtime Event recording
- user-level production traceability
- downtime opening and closing traceability
- derived downtime duration
- protected manufacturing relationships
- database-level integrity constraints
- Django administration
- automated model testing
- manual synthetic operational verification

---

# 16. FO-008 Current State

Current issue:

```text
FO-008: Create downtime event model
```

Current feature branch:

```text
feature/fo-008-downtime-events
```

Implemented migration:

```text
0006_downtimeevent
```

Current verified state:

```text
Migration applied
Django system check passing
No missing migrations detected
98 core automated tests passing
DowntimeEvent registered in Django admin
Synthetic open downtime manually verified
Duplicate open downtime rejection manually verified
Synthetic downtime closure manually verified
Derived duration manually verified
```

FO-008 does not implement:

- automatic ProductionRun pause
- automatic ProductionRun resume
- ProductionRun completion blocking
- closed-event immutability
- downtime-specific website workflow outside Django admin
- dashboard downtime metrics
- QualityInspection
- AuditEvent

Those behaviours must only be implemented through future roadmap issues that explicitly define them.

---

# 17. Current Database Architecture Summary

The current implemented core database architecture is:

```text
Product
    │
    ▼
WorkOrder
    │
    ▼
ProductionRun ◄──── ProductionLine
    │                    │
    │                    ▼
    │              ProductionArea
    │                    │
    │                    ▼
    │                   Site
    │
    ├────────────── Shift
    │
    ├────────────── ProductionEntry
    │                     │
    │                     ▼
    │                    User
    │
    └────────────── DowntimeEvent
                         │
                         ├──── DowntimeReason
                         │
                         ├──── opened_by User
                         │
                         └──── closed_by User
```

In operational terms:

1. A Product exists in ForgeOps manufacturing reference data.
2. A WorkOrder defines planned manufacturing demand.
3. A ProductionRun executes that WorkOrder on a ProductionLine during a Shift.
4. While the ProductionRun is ACTIVE, Users may record ProductionEntry transactions.
5. ProductionRun good and rejected totals are derived from ProductionEntry history.
6. While the ProductionRun is ACTIVE, a User may open a DowntimeEvent.
7. The DowntimeEvent records a controlled DowntimeReason.
8. Only one open DowntimeEvent may exist for that ProductionRun at one time.
9. Closing downtime records an end timestamp and closing User.
10. Downtime duration is derived from the recorded timestamps.
11. QualityInspection and AuditEvent remain planned future models.

This is the current database foundation after FO-008.