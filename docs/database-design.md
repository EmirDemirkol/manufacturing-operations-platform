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
- `QualityInspection.completed_by`
- `AuditEvent.user`

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
- A Production Run cannot be deleted while dependent Quality Inspections exist.
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

## QualityInspection

A Quality Inspection represents a basic quality check performed against a ProductionRun.

QualityInspection was implemented as part of FO-009.

### Attributes

- ID
- Production Run
- Result
- Notes
- Completed by
- Completed date and time
- Created date and time
- Updated date and time

### Relationships

```text
QualityInspection.production_run -> ProductionRun
QualityInspection.completed_by -> User
```

Both relationships use protected deletion when referenced records exist.

### Result Values

```text
PENDING
PASSED
FAILED
```

### Rules

- Each Quality Inspection belongs to exactly one Production Run.
- One Production Run may contain multiple Quality Inspections.
- A new Quality Inspection defaults to `PENDING`.
- `PENDING` represents an inspection that has not been completed.
- A PENDING Quality Inspection has no `completed_by` User.
- A PENDING Quality Inspection has no `completed_at` timestamp.
- `PASSED` represents a completed inspection that passed.
- `FAILED` represents a completed inspection that failed.
- A PASSED Quality Inspection requires a `completed_by` User.
- A PASSED Quality Inspection requires a `completed_at` timestamp.
- A FAILED Quality Inspection requires a `completed_by` User.
- A FAILED Quality Inspection requires a `completed_at` timestamp.
- Notes are optional.
- ProductionRun records referenced by Quality Inspections are protected from deletion.
- Users referenced through `completed_by` are protected from deletion.
- Created and updated timestamps are generated automatically.
- FO-009 does not restrict QualityInspection creation to ACTIVE Production Runs.
- FO-009 does not automatically change ProductionRun status.
- FO-009 does not determine how many Quality Inspections are required before ProductionRun completion.
- FO-009 does not block ProductionRun completion based on pending or failed Quality Inspections.
- Quality-specific application permissions remain a later workflow concern.

### Pending Example

```text
Production Run: WO-2026-0001 / LINE-A01
Result: PENDING
Completed By: blank
Completed At: blank
Notes: Synthetic pending quality inspection test for FO-009.
```

### Passed Example

```text
Production Run: WO-2026-0001 / LINE-A01
Result: PASSED
Completed By: admin
Completed At: 2026-08-08 19:07
Notes: Synthetic passed quality inspection test for FO-009.
```

### Failed Example

```text
Production Run: WO-2026-0001 / LINE-A01
Result: FAILED
Completed By: admin
Completed At: 2026-08-08 19:07
Notes: Synthetic failed quality inspection test for FO-009.
```

All examples are synthetic.

### Database Constraint

QualityInspection includes:

```text
quality_inspection_completion_state_consistent
```

This protects the consistency of inspection state.

Conceptually:

```text
PENDING
├── completed_by = null
└── completed_at = null
```

and:

```text
PASSED or FAILED
├── completed_by = populated
└── completed_at = populated
```

This prevents incomplete completion records from being stored.

### Django Administration

QualityInspection is registered in Django administration.

The current administrative list displays:

- Production Run
- Result
- Completed by
- Completed at
- Created at

The administration configuration also provides:

- result filtering
- ProductionRun status filtering
- Site and ProductionLine filtering
- completion User filtering
- timestamp filtering
- search fields
- ProductionRun autocomplete
- completion User autocomplete
- related-object query optimisation

### Manual FO-009 Verification

FO-009 was manually exercised using synthetic records through Django administration.

The manual verification demonstrated that:

1. QualityInspection appears in Django administration.
2. A PENDING QualityInspection can be created against a ProductionRun.
3. A PENDING inspection stores no `completed_by` User.
4. A PENDING inspection stores no `completed_at` timestamp.
5. A PASSED inspection without completion User and timestamp is rejected.
6. A valid PASSED inspection can be saved with `completed_by` and `completed_at`.
7. A valid FAILED inspection can be saved with `completed_by` and `completed_at`.
8. Multiple QualityInspection records may exist for the same ProductionRun.
9. Completion User and timestamp traceability are preserved.

All records used for this verification were synthetic.

---

## AuditEvent

An Audit Event represents one important action recorded in ForgeOps for operational traceability.

AuditEvent was implemented as part of FO-010.

### Attributes

- ID
- User
- Action type
- Record type
- Record identifier
- Description
- Created date and time

### Relationships

```text
AuditEvent.user -> User
```

The User relationship uses protected deletion so that a User referenced by an AuditEvent cannot be deleted while that event exists.

The affected ForgeOps record is identified using `record_type` and `record_identifier` rather than a direct foreign key to every possible auditable model.

### Action Type Values

```text
CREATED
UPDATED
ASSIGNED
STARTED
COMPLETED
CANCELLED
OPENED
CLOSED
CORRECTED
```

### Rules

- Each AuditEvent records exactly one User.
- `action_type` is limited to the controlled values defined by `AuditEvent.ActionType`.
- `record_type` is required.
- `record_identifier` is required.
- `description` is required.
- `created_at` is generated automatically.
- AuditEvent records are ordered newest first by `created_at`, then by ID.
- Existing AuditEvent records are read-only through normal Django administration.
- AuditEvent deletion is disabled through normal Django administration.
- The User referenced by an AuditEvent is protected from deletion.
- FO-010 does not require a direct foreign key from AuditEvent to every possible affected model.
- FO-010 does not automatically create AuditEvent records for every existing ForgeOps action.
- Automatic creation is intended to be added deliberately by future application workflows where explicitly defined and tested.

ForgeOps audit history is an educational operational traceability feature and must not be represented as a validated regulatory audit trail.

### Example

```text
User: admin
Action Type: STARTED
Record Type: ProductionRun
Record Identifier: WO-2026-0001 / LINE-A01
Description: Production run started.
Created At: automatically generated
```

The example is synthetic.

### Django Administration

AuditEvent is registered in Django administration.

The current administrative list displays:

- Created at
- User
- Action type
- Record type
- Record identifier
- Description

The administration configuration also provides:

- action-type filtering
- record-type filtering
- User filtering
- created-at filtering
- search across User, record type, record identifier and description
- User autocomplete
- related-User query optimisation

New synthetic AuditEvent records may be entered through Django administration for development verification.

After an AuditEvent exists, its User, action type, record type, record identifier, description and created timestamp are read-only through normal Django administration.

Normal Django administration does not provide AuditEvent deletion permission.

### Manual FO-010 Verification

FO-010 was manually exercised using synthetic records through Django administration.

The manual verification demonstrated that:

1. AuditEvent appears in Django administration.
2. A synthetic `STARTED` AuditEvent can be created.
3. The event records the responsible User.
4. The event records `ProductionRun` as its record type.
5. The event records `WO-2026-0001 / LINE-A01` as its record identifier.
6. The description is stored.
7. `created_at` is generated automatically.
8. Reopening the saved AuditEvent shows all event fields as read-only.
9. No Delete button is available for the saved AuditEvent.

All records used for this verification were synthetic.

### Implemented Migration

AuditEvent is introduced through:

```text
0008_auditevent
```

The migration:

- creates AuditEvent
- links AuditEvent to Django User using protected deletion
- adds the controlled `action_type` field
- adds `record_type`
- adds `record_identifier`
- adds `description`
- adds the automatically generated `created_at` timestamp
- applies newest-first model ordering

The migration depends on:

```text
0007_qualityinspection
```

and Django's swappable User model dependency.

### Automated Validation

FO-010 automated tests verify:

- AuditEvent creation
- the controlled action-type set
- rejection of an invalid action type through model validation
- required description
- required record type
- required record identifier
- automatic `created_at`
- User deletion protection
- User reverse relationship
- newest-first ordering
- readable string representation
- Django admin registration
- read-only existing AuditEvent fields in Django administration
- ability to enter a new synthetic AuditEvent through Django administration
- prevention of AuditEvent deletion through Django administration

All FO-010 tests use synthetic data.

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

## Quality Relationships

- One Production Run may have many Quality Inspections.
- One Quality Inspection belongs to exactly one Production Run.
- One User may complete many Quality Inspections.
- ProductionRun Quality Inspections are available through `quality_inspections`.
- Completed User relationships are available through `completed_quality_inspections`.

## Audit Relationships

- One User may be referenced by many Audit Events.
- Each Audit Event records exactly one User.
- User Audit Events are available through the `audit_events` reverse relationship.
- Each Audit Event identifies an affected record using `record_type` and `record_identifier`.
- AuditEvent does not require a direct foreign key to every possible affected model.

---

# 3. Current Relationship Summary

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
├── ProductionEntry
├── DowntimeEvent.opened_by
├── DowntimeEvent.closed_by
├── QualityInspection.completed_by
└── AuditEvent.user
```

AuditEvent identifies its affected ForgeOps record through `record_type` and `record_identifier` rather than a direct foreign key to every operational model.

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
- Production Runs referenced by Quality Inspections cannot be deleted.

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

## QualityInspection

- Each QualityInspection belongs to exactly one ProductionRun.
- One ProductionRun may contain multiple QualityInspection records.
- Inspection result values are limited to `PENDING`, `PASSED` and `FAILED`.
- New inspections default to `PENDING`.
- PENDING inspections have no completion User or completion timestamp.
- PASSED inspections require a completion User and completion timestamp.
- FAILED inspections require a completion User and completion timestamp.
- ProductionRun references use protected deletion.
- Completed User references use protected deletion.
- Notes are optional.
- Created and updated timestamps are generated automatically.

## AuditEvent

- Each AuditEvent records exactly one User.
- AuditEvent User references use protected deletion.
- Action type values are limited to `CREATED`, `UPDATED`, `ASSIGNED`, `STARTED`, `COMPLETED`, `CANCELLED`, `OPENED`, `CLOSED` and `CORRECTED`.
- `record_type` is required.
- `record_identifier` is required.
- `description` is required.
- `created_at` is generated automatically.
- Existing AuditEvent records are read-only through normal Django administration.
- AuditEvent deletion is disabled through normal Django administration.
- Affected records are identified using record type and record identifier rather than a direct foreign key to every model.
- FO-010 does not automatically log every existing ForgeOps action.

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

## Failed Inspection Count

A future operational metric may calculate:

```text
failed inspection count =
count of QualityInspection records where result = FAILED
```

Quality dashboard metrics are not part of FO-009.

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
- Should pending Quality Inspections block Production Run completion?
- Should failed Quality Inspections block Production Run completion?
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
- Quality Inspections are recorded as individual records against Production Runs.
- Quality Inspection result values are `PENDING`, `PASSED` and `FAILED`.
- New Quality Inspections default to `PENDING`.
- PENDING Quality Inspections contain no completion User or timestamp.
- PASSED and FAILED Quality Inspections require completion User and timestamp.
- One Production Run may contain multiple Quality Inspections.
- Quality Inspection completion Users are traceable.
- FO-009 does not define ProductionRun completion requirements.
- Audit Events record exactly one responsible User.
- Audit Event action types are controlled by the FO-010 action set.
- Audit Events identify affected records using record type and record identifier.
- Audit Event timestamps are generated automatically.
- Existing AuditEvent records are read-only through normal Django administration.
- AuditEvent deletion is disabled through normal Django administration.
- FO-010 does not automatically log every existing ForgeOps action.

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
        ├── QualityInspection
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
- Production Runs referenced by Quality Inspections are protected from deletion.
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

# 13. Quality Inspections

FO-009 implements QualityInspection as the transactional model for basic manufacturing quality checks.

The architecture is:

```text
ProductionRun
└── QualityInspection
    ├── result
    ├── notes
    ├── completed_by
    └── completed_at
```

## QualityInspection Key Fields

- `production_run`
- `result`
- `notes`
- `completed_by`
- `completed_at`
- `created_at`
- `updated_at`

## Result Values

```text
PENDING
PASSED
FAILED
```

## Relationships

- Each QualityInspection belongs to exactly one ProductionRun.
- One ProductionRun may contain multiple QualityInspection records.
- One User may complete multiple QualityInspection records.

Reverse relationships use:

```text
ProductionRun.quality_inspections
User.completed_quality_inspections
```

## Default State

A new QualityInspection defaults to:

```text
result = PENDING
completed_by = null
completed_at = null
```

PENDING represents an inspection that has not yet been completed.

## Completed States

A completed QualityInspection has a result of either:

```text
PASSED
FAILED
```

and requires:

```text
completed_by = populated
completed_at = populated
```

Both model validation and database integrity protection enforce this state consistency.

## Completion State Constraint

The database constraint is:

```text
quality_inspection_completion_state_consistent
```

It allows:

```text
PENDING
completed_by = null
completed_at = null
```

or:

```text
PASSED / FAILED
completed_by = populated
completed_at = populated
```

Invalid combinations are rejected.

## Traceability

QualityInspection preserves:

- which ProductionRun was inspected
- the current inspection result
- the User responsible for completing the inspection
- when the inspection was completed
- optional notes
- record creation time
- record update time

## Deletion Protection

The following relationships use protected deletion:

- ProductionRun
- completed User

A ProductionRun cannot be deleted while QualityInspection records reference it.

A User cannot be deleted while completed QualityInspection records reference that User through `completed_by`.

## Django Administration

QualityInspection is registered in Django administration.

The current administrative list displays:

- Production Run
- Result
- Completed by
- Completed at
- Created at

Search, filtering, autocomplete and related-object optimisation are configured for practical inspection.

## Manual Synthetic Verification

FO-009 was manually tested through Django administration using synthetic data.

The verified records included:

```text
Result: PENDING
Completed by: blank
Completed at: blank
```

```text
Result: PASSED
Completed by: admin
Completed at: populated
```

```text
Result: FAILED
Completed by: admin
Completed at: populated
```

A deliberately invalid PASSED QualityInspection with no completion User and no completion timestamp was rejected with validation errors.

Multiple QualityInspection records were successfully recorded against the same synthetic ProductionRun.

## Implemented Migration

QualityInspection is introduced through:

```text
0007_qualityinspection
```

The migration:

- creates QualityInspection
- links QualityInspection to ProductionRun
- links optional `completed_by` to Django User
- adds the controlled `result` field
- defaults result to `PENDING`
- adds optional notes
- adds optional `completed_at`
- adds creation and update timestamps
- adds the completion-state consistency database constraint

The migration depends on:

```text
0006_downtimeevent
```

and Django's swappable User model dependency.

## Automated Validation

FO-009 automated tests verify:

- expected QualityInspection relationships
- default PENDING state
- optional notes
- creation timestamps
- update timestamps
- multiple QualityInspections for one ProductionRun
- valid PENDING inspections
- valid PASSED inspections
- valid FAILED inspections
- rejection of invalid result values
- rejection of PENDING inspections with `completed_by`
- rejection of PENDING inspections with `completed_at`
- PASSED inspection completion User requirements
- PASSED inspection completion timestamp requirements
- FAILED inspection completion User requirements
- FAILED inspection completion timestamp requirements
- database completion-state consistency
- ProductionRun deletion protection
- completed User deletion protection
- completed User reverse relationship
- readable string representation
- Django admin registration

All FO-009 tests use synthetic manufacturing data.

FO-009 does not implement ProductionRun completion blocking, quality-specific website workflows, automatic ProductionRun status changes or quality approval workflows.

---

# 14. Migration History

The current ForgeOps core migration sequence is:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

All eight migrations are currently applied in the local SQLite development database.

---

# 15. Current Test Milestone

The current full Core test milestone is:

```text
Ran 162 tests
OK
```

Historical milestones include:

```text
FO-005: 34 tests
FO-006: 58 tests
FO-007: 77 tests
FO-008: 98 tests
FO-009: 118 tests
FO-010: 133 tests
FO-011: 147 tests
FO-012: 162 tests
```

FO-010 added 15 AuditEvent tests while preserving the existing 118-test FO-009 baseline.

FO-011 added 14 WorkOrder interface tests while preserving the existing 133-test FO-010 baseline.

FO-012 adds 15 ProductionRun interface tests while preserving the existing 147-test FO-011 baseline.

---

# 16. Current Implementation Status

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
QualityInspection
AuditEvent
```

The current implemented operational structure is:

```text
Site
└── ProductionArea
    └── ProductionLine
        └── ProductionRun
            ├── ProductionEntry
            ├── DowntimeEvent
            └── QualityInspection

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
├── DowntimeEvent.closed_by
├── QualityInspection.completed_by
└── AuditEvent.user
```

AuditEvent identifies affected ForgeOps records through `record_type` and `record_identifier` rather than direct foreign keys to each operational model.

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
- Production Run records
- incremental Production Entry recording
- derived ProductionRun quantity totals
- transactional Downtime Event recording
- Quality Inspection recording
- PENDING, PASSED and FAILED inspection states
- quality completion User traceability
- quality completion timestamp traceability
- AuditEvent operational traceability records
- controlled AuditEvent action types
- AuditEvent User traceability
- indirect affected-record identification using record type and record identifier
- read-only existing AuditEvent records in Django administration
- prevention of AuditEvent deletion through normal Django administration
- user-level production traceability
- downtime opening and closing traceability
- derived downtime duration
- protected manufacturing relationships
- database-level integrity constraints
- Django administration
- automated model testing
- manual synthetic operational verification

The current ForgeOps application layer additionally supports:

- WorkOrder list interface
- WorkOrder detail interface
- WorkOrder creation interface
- authenticated WorkOrder access
- role-controlled WorkOrder creation
- WorkOrder status filtering
- WorkOrder Product filtering
- combined WorkOrder filtering
- clearing WorkOrder filters
- active Product selection during WorkOrder creation
- display of related ProductionRuns from a WorkOrder detail page
- server-side prevention of unauthorised WorkOrder creation
- ProductionRun list interface
- ProductionRun detail interface
- WorkOrder-scoped ProductionRun creation
- authenticated ProductionRun access
- role-controlled ProductionRun creation
- ProductionRun status filtering
- ProductionRun WorkOrder filtering
- ProductionRun Production Line filtering
- ProductionRun Shift filtering
- combined ProductionRun filtering
- clearing ProductionRun filters
- active Production Line selection during ProductionRun creation
- active Shift selection during ProductionRun creation
- server-side WorkOrder assignment during ProductionRun creation
- display of ProductionRun derived quantity information
- navigation between WorkOrders and ProductionRuns
- server-side prevention of unauthorised ProductionRun creation

---

# 17. FO-010 Current State

Issue:

```text
FO-010: Create audit event model
```

GitHub issue:

```text
#19
```

Implemented migration:

```text
0008_auditevent
```

Verified state:

```text
Migration applied
Django system check passing
AuditEvent registered in Django admin
Synthetic STARTED AuditEvent manually created
Responsible User manually verified
Record type and record identifier manually verified
Automatic created timestamp manually verified
Existing AuditEvent fields manually verified as read-only
AuditEvent delete option manually verified as unavailable
15 FO-010 AuditEvent tests passing
133 core automated tests passing
```

FO-010 does not implement:

- a validated regulatory audit trail
- electronic signatures
- 21 CFR Part 11 compliance
- automatic logging of every Django model change
- automatic AuditEvent creation for every existing ForgeOps action
- machine-generated audit records
- REST API audit logging
- SIEM integration
- audit export workflows
- audit dashboards
- audit retention or archival workflows
- ProductionRun workflow changes
- QualityInspection workflow changes
- DowntimeEvent workflow changes
- machine integration
- real manufacturing data

Those behaviours must only be implemented through future roadmap issues that explicitly define them.

---

# 18. FO-011 Current State

Issue:

```text
FO-011: Build work order management interface
```

GitHub issue:

```text
#21
```

FO-011 introduced the first dedicated WorkOrder management workflow in the ForgeOps website.

The existing WorkOrder database model remained unchanged.

FO-011 did not introduce a database migration.

## Implemented WorkOrder Interface

FO-011 implements:

- WorkOrder list page
- WorkOrder detail page
- WorkOrder creation page
- authenticated access to WorkOrder pages
- role-controlled WorkOrder creation
- WorkOrder status filtering
- WorkOrder Product filtering
- combined filtering
- clear-filter behaviour
- WorkOrder form validation
- active Product selection during WorkOrder creation
- related ProductionRun display on the WorkOrder detail page

## WorkOrder List

The WorkOrder list is available at:

```text
/work-orders/
```

The list displays:

- WorkOrder number
- Product
- planned quantity
- status
- due date
- creation timestamp

Each WorkOrder number links to its detail page.

## WorkOrder Filtering

The WorkOrder list supports filtering by:

- status
- Product

Filtering uses GET query parameters.

Example:

```text
/work-orders/?status=DRAFT&product=1
```

Status and Product filters can be used individually or together.

The Clear action removes the active filters and restores the complete WorkOrder list.

Manual verification demonstrated:

```text
Status: DRAFT
Product: PRD-1001
Result: WO-2026-0002
```

The existing RELEASED WorkOrder was excluded from that filtered result.

Clearing the filters restored both synthetic WorkOrders.

## WorkOrder Detail

The WorkOrder detail page displays:

- WorkOrder number
- Product
- planned quantity
- status
- due date
- active state
- creation timestamp
- update timestamp
- notes
- related ProductionRuns

Related ProductionRuns link into the ProductionRun detail workflow.

The WorkOrder detail page also provides the ProductionRun creation action to Users permitted by FO-012.

## WorkOrder Creation

The WorkOrder creation page is available at:

```text
/work-orders/new/
```

The creation workflow uses a Django ModelForm based on the existing WorkOrder model.

The form supports:

- WorkOrder number
- Product
- planned quantity
- status
- due date
- notes

Only active Product records are available for selection.

Inactive Product records are excluded from the Product selection queryset.

A successfully created WorkOrder redirects to its WorkOrder detail page.

## WorkOrder Creation Permissions

WorkOrder creation is permitted by the FO-011 permission logic for:

```text
Production Supervisor
System Administrator
Django superuser
```

The existing Django Group architecture remains the source of role permissions.

FO-011 does not introduce a second permission system.

Operators may view the WorkOrder list but cannot create WorkOrders.

The Create Work Order action is hidden from Operators.

Direct unauthorised access to:

```text
/work-orders/new/
```

returns:

```text
403 Forbidden
```

## Manual FO-011 Verification

FO-011 was manually exercised through the ForgeOps website using synthetic manufacturing data.

The manual verification demonstrated that:

1. The WorkOrder list page loads successfully.
2. Existing synthetic WorkOrders are displayed.
3. WorkOrder numbers link to WorkOrder detail pages.
4. WorkOrder detail information is displayed correctly.
5. Related ProductionRuns are displayed from the WorkOrder detail workflow.
6. A new synthetic WorkOrder can be created successfully.
7. Successful creation redirects to the new WorkOrder detail page.
8. Duplicate WorkOrder numbers are rejected.
9. Planned quantity of zero is rejected.
10. Django superuser can create WorkOrders.
11. Production Supervisor can access the WorkOrder creation workflow.
12. Operator can access the WorkOrder list.
13. Operator does not receive the Create Work Order action.
14. Operator direct access to the creation URL returns 403 Forbidden.
15. Status filtering works.
16. Product filtering works.
17. Status and Product filtering can be combined.
18. Clearing filters restores the full WorkOrder list.

All records used for manual FO-011 verification were synthetic.

## Automated FO-011 Validation

The dedicated FO-011 test class is:

```text
WorkOrderInterfaceTests
```

The dedicated test run produced:

```text
Found 14 test(s)
Ran 14 tests
OK
```

The full Core test suite after FO-011 was:

```text
Ran 147 tests
OK
```

FO-011 therefore added 14 WorkOrder interface tests while preserving the existing 133-test FO-010 baseline.

## Migration Verification

FO-011 did not modify the database schema.

No FO-011 migration was required.

## FO-011 Files Added

```text
core/forms.py
core/templates/core/work_order_list.html
core/templates/core/work_order_detail.html
core/templates/core/work_order_form.html
```

## FO-011 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
docs/database-design.md
```

## FO-011 Does Not Implement

FO-011 does not implement:

- WorkOrder editing
- WorkOrder deletion
- ProductionRun lifecycle transitions
- ProductionRun assignment
- ProductionRun start workflow
- ProductionRun pause workflow
- ProductionRun completion workflow
- Operator assignment
- ProductionEntry website workflow
- downtime website workflow
- QualityInspection website workflow
- automatic AuditEvent creation for WorkOrder actions
- dashboard analytics
- REST API endpoints
- machine integration
- real manufacturing data

---

# 19. FO-012 Current State

Issue:

```text
FO-012: Build production run management interface
```

Feature branch:

```text
feature/fo-012-production-run-interface
```

FO-012 introduces the first dedicated ProductionRun website management interface.

FO-012 builds on the existing ProductionRun model created before this issue.

The existing ProductionRun database schema remains unchanged.

FO-012 does not introduce a database migration.

## Implemented ProductionRun Interface

FO-012 implements:

- ProductionRun list page
- ProductionRun detail page
- WorkOrder-scoped ProductionRun creation page
- ProductionRun creation from a WorkOrder detail page
- authenticated access to ProductionRun pages
- role-controlled ProductionRun creation
- ProductionRun status filtering
- ProductionRun WorkOrder filtering
- ProductionRun Production Line filtering
- ProductionRun Shift filtering
- combined filtering
- clear-filter behaviour
- active Production Line selection during ProductionRun creation
- active Shift selection during ProductionRun creation
- server-side WorkOrder assignment
- related WorkOrder navigation
- derived ProductionRun quantity display

## ProductionRun List

The ProductionRun list is available at:

```text
/production-runs/
```

The list displays:

- ProductionRun identifier
- WorkOrder
- Production Line
- Shift
- status
- total recorded quantity
- completion percentage
- creation timestamp

Each ProductionRun identifier links to its detail page.

The displayed quantity information is derived from the existing ProductionRun properties and related ProductionEntry records.

FO-012 does not introduce duplicate stored quantity fields.

## ProductionRun Filtering

The ProductionRun list supports filtering by:

- status
- WorkOrder
- Production Line
- Shift

Filtering uses GET query parameters.

The filters may be used individually or together.

The Clear action removes active filters and restores the complete ProductionRun list.

Manual verification demonstrated status filtering using synthetic ProductionRuns.

For example:

```text
Status: PLANNED
Result: Production Run #2
```

and:

```text
Status: ACTIVE
Result: Production Run #1
```

The list correctly excluded ProductionRuns whose status did not match the selected filter.

## ProductionRun Detail

A ProductionRun detail page is available through:

```text
/production-runs/<id>/
```

The detail page displays:

- ProductionRun identifier
- WorkOrder
- Product
- Production Line
- Shift
- status
- started timestamp
- ended timestamp
- creation timestamp
- good quantity
- rejected quantity
- total recorded quantity
- completion percentage
- notes

The page also provides navigation to:

- ProductionRun list
- related WorkOrder
- dashboard

The quantity values displayed by the page use the existing ProductionRun derived properties.

FO-012 does not redefine the unresolved final business definition of completion percentage documented elsewhere in this design.

## ProductionRun Creation

A ProductionRun is created in the context of an existing WorkOrder.

The creation URL uses:

```text
/work-orders/<work_order_id>/production-runs/new/
```

The WorkOrder is determined by the URL and server-side view logic.

The User does not independently select a different WorkOrder through the ProductionRun creation form.

The creation form supports:

- Production Line
- Shift
- notes

A newly created ProductionRun uses the existing model default status:

```text
PLANNED
```

A successful creation redirects to the new ProductionRun detail page.

Manual verification created a synthetic ProductionRun with:

```text
Work Order: WO-2026-0001
Production Line: LINE-A01 - Line A
Shift: Night Shift
Status: PLANNED
Notes: Synthetic FO-012 Production Run creation test.
```

The created ProductionRun remained attached to the WorkOrder supplied by the creation URL.

## Active Reference Data

ProductionRun creation limits selectable reference data to active records.

Only active Production Lines are available in the creation form.

Only active Shifts are available in the creation form.

Inactive Production Lines and inactive Shifts are excluded from the form querysets.

The existing database relationships and model validation remain unchanged.

## ProductionRun Creation Permissions

ProductionRun creation is permitted by the FO-012 permission logic for:

```text
Production Supervisor
System Administrator
Django superuser
```

The existing Django Group architecture remains the source of role permissions.

FO-012 does not introduce a second permission system.

Operators may inspect ProductionRun information but cannot create ProductionRuns.

Direct unauthorised access to a ProductionRun creation URL returns:

```text
403 Forbidden
```

This prevents an unauthorised User from bypassing the interface by manually entering a creation URL.

## WorkOrder Integration

FO-012 extends the existing WorkOrder detail page.

The WorkOrder detail page now:

- lists related ProductionRuns
- links each displayed ProductionRun to its ProductionRun detail page
- provides a Production Runs navigation action
- provides a Create Production Run action to authorised Users

ProductionRun creation remains scoped to the WorkOrder being viewed.

FO-012 therefore connects the existing planning and execution records through the website without changing the database relationship.

Conceptually:

```text
WorkOrder
    │
    ├── View related ProductionRuns
    │
    └── Create ProductionRun
            │
            ▼
      ProductionRun Detail
```

## Manual FO-012 Verification

FO-012 was manually exercised through the ForgeOps website using synthetic manufacturing data.

The manual verification demonstrated that:

1. The ProductionRun list page loads successfully.
2. Existing synthetic ProductionRuns are displayed.
3. ProductionRun identifiers link to ProductionRun detail pages.
4. ProductionRun detail information is displayed correctly.
5. The related WorkOrder is displayed.
6. The related Product is displayed.
7. Production Line and Shift information are displayed.
8. ProductionRun status is displayed.
9. Existing derived quantity information is displayed.
10. A Production Supervisor can create a new ProductionRun from a WorkOrder.
11. A newly created ProductionRun belongs to the requested WorkOrder.
12. A newly created ProductionRun defaults to PLANNED.
13. Successful creation redirects to the ProductionRun detail page.
14. Operator direct access to the ProductionRun creation URL returns 403 Forbidden.
15. Status filtering works.
16. WorkOrder filtering works.
17. Production Line filtering works.
18. Shift filtering works.
19. ProductionRun filters may be combined.
20. Clearing filters restores the complete ProductionRun list.
21. Only active Production Lines are offered during creation.
22. Only active Shifts are offered during creation.
23. WorkOrder detail displays its related ProductionRuns.
24. WorkOrder detail provides ProductionRun creation to an authorised User.

All records used for manual FO-012 verification were synthetic.

## Automated FO-012 Validation

FO-012 adds automated ProductionRun interface tests in:

```text
core/tests.py
```

The dedicated FO-012 test class is:

```text
ProductionRunInterfaceTests
```

The dedicated test run produced:

```text
Found 15 test(s)
Ran 15 tests
OK
```

FO-012 automated tests verify:

- ProductionRun list requires authentication
- authenticated Operator can view the ProductionRun list
- ProductionRun detail page displays ProductionRun information
- Production Supervisor can access the ProductionRun creation page
- Operator cannot access the ProductionRun creation page
- Production Supervisor can create a valid ProductionRun
- created ProductionRun belongs to the requested WorkOrder
- Production Line is required during creation
- Shift is required during creation
- inactive Production Lines are excluded from the creation form
- inactive Shifts are excluded from the creation form
- ProductionRun list can filter by status
- ProductionRun list can filter by WorkOrder
- ProductionRun list can filter by Production Line
- ProductionRun list can filter by Shift

The full Core test suite after FO-012 is:

```text
Ran 162 tests
OK
```

FO-012 therefore adds 15 ProductionRun interface tests while preserving the existing 147-test FO-011 baseline.

## Migration Verification

FO-012 does not modify the database schema.

Verification produced:

```text
python manage.py makemigrations --check --dry-run
No changes detected
```

No FO-012 migration is required.

The current migration sequence remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

## FO-012 Files Added

```text
core/templates/core/production_run_list.html
core/templates/core/production_run_detail.html
core/templates/core/production_run_form.html
```

## FO-012 Files Updated

```text
core/forms.py
core/views.py
core/urls.py
core/tests.py
core/templates/core/work_order_detail.html
docs/database-design.md
```

## FO-012 Does Not Implement

FO-012 does not implement:

- ProductionRun editing
- ProductionRun deletion
- ProductionRun start workflow
- ProductionRun pause workflow
- ProductionRun resume workflow
- ProductionRun completion workflow
- ProductionRun cancellation workflow
- Operator assignment
- ProductionEntry website workflow
- downtime website workflow
- QualityInspection website workflow
- automatic AuditEvent creation for ProductionRun actions
- automatic WorkOrder status changes
- machine integration
- REST API endpoints
- dashboard analytics
- real manufacturing data

Existing ProductionRun model rules remain authoritative.

Lifecycle behaviour must only be introduced by future roadmap issues that explicitly define and test those transitions.

## FO-012 Verified State

```text
FO-012: Build production run management interface
ProductionRun list implemented
ProductionRun detail implemented
WorkOrder-scoped ProductionRun creation implemented
ProductionRun creation from WorkOrder detail implemented
ProductionRun status filtering implemented
ProductionRun WorkOrder filtering implemented
ProductionRun Production Line filtering implemented
ProductionRun Shift filtering implemented
Active Production Line selection implemented
Active Shift selection implemented
Server-side WorkOrder assignment implemented
Production Supervisor creation permission implemented
System Administrator creation permission implemented in permission logic
Django superuser creation permission implemented
Operator ProductionRun read access implemented
Operator creation access blocked
Manual synthetic verification completed
15 FO-012 ProductionRun interface tests passing
162 core automated tests passing
No database migration required
```

---

# 20. Current Database and Application Architecture Summary

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
    ├────────────── DowntimeEvent
    │                     │
    │                     ├──── DowntimeReason
    │                     │
    │                     ├──── opened_by User
    │                     │
    │                     └──── closed_by User
    │
    └────────────── QualityInspection
                          │
                          └──── completed_by User

User
└────────────── AuditEvent
                    ├──── action_type
                    ├──── record_type
                    └──── record_identifier
```

AuditEvent identifies an affected ForgeOps record using `record_type` and `record_identifier`; it does not require a direct foreign key to every operational model.

The current WorkOrder and ProductionRun website workflow is:

```text
Authenticated User
        │
        ▼
WorkOrder List
        │
        ├──── Status Filter
        │
        ├──── Product Filter
        │
        └──── WorkOrder Detail
                 │
                 ├──── Related ProductionRuns
                 │
                 └──── Create ProductionRun
                          │
                          ▼
                  ProductionRun Detail

Authenticated User
        │
        ▼
ProductionRun List
        │
        ├──── Status Filter
        ├──── WorkOrder Filter
        ├──── Production Line Filter
        ├──── Shift Filter
        │
        └──── ProductionRun Detail
```

WorkOrder creation permissions are:

```text
Production Supervisor
System Administrator
Django Superuser
        │
        ▼
Create WorkOrder
        │
        ▼
WorkOrder Validation
        │
        ▼
WorkOrder Detail
```

ProductionRun creation permissions are:

```text
Production Supervisor
System Administrator
Django Superuser
        │
        ▼
WorkOrder Detail
        │
        ▼
Create ProductionRun
        │
        ├──── Active Production Line
        ├──── Active Shift
        └──── WorkOrder fixed server-side
        │
        ▼
ProductionRun Detail
```

Operators may inspect WorkOrders and ProductionRuns:

```text
Operator
   │
   ├──── WorkOrder List
   │       │
   │       ▼
   │   WorkOrder Detail
   │
   └──── ProductionRun List
           │
           ▼
       ProductionRun Detail
```

but cannot create either record type through the restricted creation workflows:

```text
Operator
   │
   X
Create WorkOrder
```

```text
Operator
   │
   X
Create ProductionRun
```

Unauthorised direct creation access returns:

```text
403 Forbidden
```

In operational terms:

1. A Product exists in ForgeOps manufacturing reference data.
2. A WorkOrder defines planned manufacturing demand.
3. Authenticated ForgeOps Users may inspect WorkOrders through the WorkOrder list.
4. WorkOrders may be filtered by status.
5. WorkOrders may be filtered by Product.
6. WorkOrder filters may be combined and cleared.
7. Production Supervisors, System Administrators and Django superusers may create WorkOrders according to FO-011 permission logic.
8. Operators may inspect WorkOrders but cannot create them.
9. New WorkOrders may reference only active Products through the FO-011 creation form.
10. WorkOrder creation continues to use existing WorkOrder validation and integrity rules.
11. A WorkOrder detail page exposes its related ProductionRuns.
12. Authorised Users may create a ProductionRun from a WorkOrder detail page.
13. ProductionRun creation fixes the WorkOrder server-side from the URL.
14. New ProductionRuns default to PLANNED through the existing model default.
15. New ProductionRuns may select only active Production Lines.
16. New ProductionRuns may select only active Shifts.
17. Authenticated Users may inspect ProductionRuns through the ProductionRun list.
18. ProductionRuns may be filtered by status.
19. ProductionRuns may be filtered by WorkOrder.
20. ProductionRuns may be filtered by Production Line.
21. ProductionRuns may be filtered by Shift.
22. ProductionRun filters may be combined and cleared.
23. ProductionRun detail pages expose WorkOrder, Product, Production Line, Shift, status, timestamps, notes and derived quantity information.
24. Operators may inspect ProductionRuns but cannot create them.
25. A ProductionRun executes a WorkOrder on a ProductionLine during a Shift.
26. While the ProductionRun is ACTIVE, Users may record ProductionEntry transactions through existing data-layer functionality.
27. ProductionRun good and rejected totals are derived from ProductionEntry history.
28. While the ProductionRun is ACTIVE, a User may open a DowntimeEvent through existing data-layer functionality.
29. The DowntimeEvent records a controlled DowntimeReason.
30. Only one open DowntimeEvent may exist for that ProductionRun at one time.
31. Closing downtime records an end timestamp and closing User.
32. Downtime duration is derived from the recorded timestamps.
33. A ProductionRun may contain multiple QualityInspection records.
34. New QualityInspection records default to PENDING.
35. PENDING Quality Inspections contain no completion User or completion timestamp.
36. PASSED and FAILED Quality Inspections require both a completion User and completion timestamp.
37. QualityInspection completion state is protected by model validation and a database constraint.
38. QualityInspection completion requirements do not currently affect ProductionRun completion.
39. AuditEvent records important ForgeOps actions together with the responsible User.
40. AuditEvent action types use the controlled FO-010 action set.
41. AuditEvent identifies the affected record using record type and record identifier.
42. AuditEvent creation timestamps are generated automatically.
43. Existing AuditEvent records are read-only through normal Django administration.
44. AuditEvent deletion is disabled through normal Django administration.
45. FO-010 does not automatically generate AuditEvent records for every existing ForgeOps action.
46. FO-011 does not automatically create AuditEvent records for WorkOrder website actions.
47. FO-012 does not automatically create AuditEvent records for ProductionRun website actions.
48. FO-012 does not implement ProductionRun lifecycle transitions.
49. FO-012 does not modify the existing database schema.

This is the current ForgeOps database and application foundation after FO-012.

# 21. FO-013 Current State

## FO-013: Implement Production Run Start Workflow

FO-013 introduces the first ProductionRun lifecycle action through the ForgeOps website.

The existing ProductionRun model remains unchanged.

No database migration is required.

## ProductionRun Start Workflow

An authorised User may start an existing ProductionRun through the ProductionRun detail page.

The workflow is:

```text
PLANNED ProductionRun
        |
        v
Start Production Run
        |
        v
POST request
        |
        v
Permission validation
        |
        v
ProductionRun state validation
        |
        v
ACTIVE
```

Starting a ProductionRun changes:

```text
status     -> ACTIVE
started_at -> current application timestamp
ended_at   -> None
```

The ProductionRun is then redirected back to its detail page.

## Start Permissions

ProductionRun start permission is granted to:

- Production Supervisor
- System Administrator
- Django superuser

Operators may inspect ProductionRuns but may not start them.

Unauthorised start attempts return:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

## HTTP Method Requirement

ProductionRun lifecycle changes must not occur through a normal GET request.

The start endpoint therefore requires:

```text
POST
```

A GET request to the start endpoint is rejected with:

```text
403 Forbidden
```

This prevents ProductionRun state changes from being triggered through ordinary page navigation.

## ProductionRun State Requirement

Only ProductionRuns currently in:

```text
PLANNED
```

status may be started.

A ProductionRun already in:

```text
ACTIVE
```

status cannot be started again.

Other ProductionRun lifecycle states also remain ineligible for the FO-013 start action.

## Active ProductionRun Constraint

The existing ProductionRun model already enforces:

```text
Only one ACTIVE ProductionRun may exist for one WorkOrder at a time.
```

FO-013 preserves this rule in the website workflow.

Before starting a PLANNED ProductionRun, the application checks whether another ACTIVE ProductionRun already exists for the same WorkOrder.

If another ACTIVE ProductionRun exists, the start request is rejected with:

```text
403 Forbidden
```

The PLANNED ProductionRun remains unchanged.

This application-level validation prevents the existing database uniqueness constraint from surfacing as an unhandled ValidationError during the website workflow.

The database constraint remains authoritative.

## ProductionRun Detail Integration

For an authorised User, the ProductionRun detail page displays:

```text
Start Production Run
```

only when the ProductionRun status is:

```text
PLANNED
```

After a successful start:

- status displays as Active
- `started_at` displays the generated start timestamp
- `ended_at` remains empty
- the Start Production Run action disappears

The detail page therefore reflects the current lifecycle state of the ProductionRun.

## Manual FO-013 Verification

FO-013 was manually verified using synthetic manufacturing data.

Manual verification demonstrated:

- A PLANNED ProductionRun displays the Start Production Run action for an authorised User.
- Starting a valid PLANNED ProductionRun succeeds.
- The ProductionRun changes from PLANNED to ACTIVE.
- `started_at` is populated automatically.
- `ended_at` remains empty.
- The Start Production Run action disappears after successful start.
- An existing ACTIVE ProductionRun cannot be started again.
- A second ProductionRun for the same WorkOrder cannot be started while another ACTIVE ProductionRun exists.
- The conflicting start attempt returns 403 Forbidden instead of an unhandled ValidationError.
- The conflicting ProductionRun remains PLANNED.
- Existing ProductionRun database constraints remain unchanged.

All records used for manual FO-013 verification were synthetic.

Example successful transition:

```text
Production Run #3
Work Order: WO-2026-0003

Before:
Status: PLANNED
Started: Not started
Ended: Not ended

After:
Status: ACTIVE
Started: generated timestamp
Ended: Not ended
```

## Automated FO-013 Validation

FO-013 adds seven ProductionRun start workflow tests to:

```text
core/tests.py
```

The existing ProductionRun interface test class now contains:

```text
22 tests
```

The dedicated interface test run produced:

```text
Found 22 test(s)
Ran 22 tests
OK
```

FO-013 automated tests verify:

- authorised User sees the Start Production Run action for a PLANNED ProductionRun
- Start Production Run action is hidden for an ACTIVE ProductionRun
- Operator cannot start a ProductionRun
- ProductionRun start requires POST
- Production Supervisor may start a valid PLANNED ProductionRun
- an ACTIVE ProductionRun cannot be started again
- a second ACTIVE ProductionRun for the same WorkOrder is blocked

## Full Core Validation

The full Core test suite after FO-013 produced:

```text
Ran 169 tests
OK
```

FO-013 therefore adds seven automated tests while preserving the existing 162-test FO-012 baseline.

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-013 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-013 migration is required.

## FO-013 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
docs/database-design.md
```

## FO-013 Acceptance Criteria Verified

- ProductionRun start workflow is implemented.
- Only authorised Users may start ProductionRuns.
- Start operation requires POST.
- Only PLANNED ProductionRuns may be started.
- Successful start changes status to ACTIVE.
- Successful start records `started_at` automatically.
- Successful start leaves `ended_at` empty.
- Start action is displayed only for eligible PLANNED ProductionRuns.
- Existing ACTIVE ProductionRuns cannot be started again.
- A second ACTIVE ProductionRun for the same WorkOrder is blocked.
- Active-run conflicts return controlled 403 responses.
- Existing database constraints remain authoritative.
- No database migration is introduced.
- Manual verification uses synthetic manufacturing data.
- 22 ProductionRun interface tests pass.
- 169 Core tests pass.
- Django system checks pass.
- Migration drift check passes.
- Git whitespace validation passes.

## FO-013 Out of Scope

FO-013 does not implement:

- ProductionRun pause workflow
- ProductionRun resume workflow
- ProductionRun completion workflow
- ProductionRun cancellation workflow
- ProductionRun editing
- ProductionRun deletion
- Operator assignment
- ProductionEntry website workflow
- DowntimeEvent website workflow
- QualityInspection website workflow
- automatic AuditEvent creation for ProductionRun start actions
- automatic WorkOrder status changes
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 22. FO-014 Current State

## FO-014: Implement Production Run Pause Workflow

FO-014 introduces the ProductionRun pause lifecycle action through the ForgeOps website.

The existing ProductionRun model remains unchanged.

No database migration is required because the existing ProductionRun status set already includes:

```text
PAUSED
```

## ProductionRun Pause Workflow

An authorised User may pause an existing ACTIVE ProductionRun through the ProductionRun detail page.

The workflow is:

```text
ACTIVE ProductionRun
        |
        v
Pause Production Run
        |
        v
POST request
        |
        v
Permission validation
        |
        v
ProductionRun state validation
        |
        v
PAUSED
```

Pausing a ProductionRun changes:

```text
status -> PAUSED
```

The existing lifecycle timestamps are preserved.

Successful pause therefore leaves:

```text
started_at -> unchanged
ended_at   -> unchanged
```

Pausing a ProductionRun does not complete or end the run.

After a successful pause, the User is redirected back to the ProductionRun detail page.

## Pause Permissions

ProductionRun pause permission is granted to:

- Production Supervisor
- System Administrator
- Django superuser

Operators may inspect ProductionRuns but may not pause them.

Unauthorised pause attempts return:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

FO-014 does not introduce a separate permission system.

## HTTP Method Requirement

ProductionRun pause changes application state and therefore requires:

```text
POST
```

The ProductionRun detail page submits the pause action through a POST form protected by Django CSRF validation.

A direct GET request to the pause endpoint is rejected with:

```text
403 Forbidden
```

The ProductionRun remains unchanged.

## ProductionRun State Requirement

Only ProductionRuns currently in:

```text
ACTIVE
```

status may be paused.

Pause attempts are rejected for ProductionRuns in:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

Invalid transition attempts return:

```text
403 Forbidden
```

and do not change the ProductionRun state.

## ProductionRun Detail Integration

For an authorised User, the ProductionRun detail page displays:

```text
Pause Production Run
```

only when the ProductionRun status is:

```text
ACTIVE
```

After a successful pause:

- status displays as Paused
- the existing `started_at` timestamp remains unchanged
- `ended_at` remains unchanged
- the Pause Production Run action disappears
- the Start Production Run action remains unavailable

The ProductionRun detail page therefore reflects the current lifecycle state of the ProductionRun.

## Existing ProductionEntry Behaviour

FO-014 does not introduce new ProductionEntry validation.

The existing ProductionEntry model already permits new entries only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a PAUSED ProductionRun naturally rejects new ProductionEntry records through the existing model rule.

FO-014 does not duplicate this validation in the pause view.

## Existing DowntimeEvent Behaviour

FO-014 does not introduce new DowntimeEvent validation.

The existing DowntimeEvent model already permits new downtime events to be opened only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a PAUSED ProductionRun naturally rejects new DowntimeEvent creation through the existing model rule.

FO-014 does not duplicate this validation in the pause view.

## Downtime Independence

FO-014 does not automatically create a DowntimeEvent when a ProductionRun is paused.

Existing DowntimeEvent behaviour remains independent from the ProductionRun pause workflow.

The unresolved business questions around:

```text
automatic pause when downtime opens
automatic resume when downtime closes
```

remain unresolved and are not changed by FO-014.

## AuditEvent Behaviour

FO-014 does not automatically create an AuditEvent when a ProductionRun is paused.

The existing FO-010 AuditEvent architecture remains unchanged.

Automatic lifecycle audit logging remains reserved for a future issue that explicitly defines and tests that behaviour.

## Manual FO-014 Verification

FO-014 was manually verified through the ForgeOps website using synthetic manufacturing data.

The primary manual test used:

```text
Production Run #3
Work Order: WO-2026-0003
```

Before the pause action:

```text
Status: ACTIVE
Started: 13 Aug 2026, 5:23 p.m.
Ended: Not ended
```

The authorised User was presented with:

```text
Pause Production Run
```

After submitting the pause action:

```text
Status: PAUSED
Started: 13 Aug 2026, 5:23 p.m.
Ended: Not ended
```

The test demonstrated that:

1. An ACTIVE ProductionRun displays the Pause Production Run action to an authorised User.
2. The pause action submits successfully through POST.
3. The ProductionRun changes from ACTIVE to PAUSED.
4. The existing `started_at` timestamp remains unchanged.
5. `ended_at` remains unchanged.
6. The Pause Production Run action disappears after the transition.
7. The Start Production Run action is not displayed for the PAUSED run.
8. Direct GET access to the pause endpoint returns 403 Forbidden.
9. The Operator role does not receive the Pause Production Run action for an ACTIVE ProductionRun.

Operator permission behaviour was manually verified using:

```text
operator_demo
```

against synthetic:

```text
Production Run #1
```

Production Run #1 remained ACTIVE while the Operator received no Pause Production Run action.

All records used for manual FO-014 verification were synthetic.

## Automated FO-014 Validation

FO-014 adds nine ProductionRun pause workflow tests to:

```text
core/tests.py
```

The existing ProductionRun interface test class now contains:

```text
31 tests
```

The dedicated interface test run produced:

```text
Ran 31 tests
OK
```

FO-014 automated tests verify:

- Production Supervisor sees the Pause Production Run action for an ACTIVE ProductionRun
- Pause Production Run action is hidden for a PLANNED ProductionRun
- Operator cannot pause a ProductionRun
- ProductionRun pause requires POST
- Production Supervisor may pause a valid ACTIVE ProductionRun
- successful pause preserves `started_at`
- successful pause preserves `ended_at`
- a PAUSED ProductionRun cannot be paused again
- a PLANNED ProductionRun cannot be paused
- a COMPLETED ProductionRun cannot be paused
- a CANCELLED ProductionRun cannot be paused

Several related assertions are combined within individual tests.

## Full Core Validation

The full Core test suite after FO-014 produced:

```text
Ran 178 tests
OK
```

FO-014 therefore adds nine automated tests while preserving the existing 169-test FO-013 baseline.

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-014 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-014 migration is required.

## FO-014 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
docs/database-design.md
```

## FO-014 Acceptance Criteria Verified

- ProductionRun pause workflow is implemented.
- Only authorised Users may pause ProductionRuns.
- Pause operation requires POST.
- Only ACTIVE ProductionRuns may be paused.
- Successful pause changes status to PAUSED.
- Successful pause preserves `started_at`.
- Successful pause preserves `ended_at`.
- Pause action is displayed only for eligible ACTIVE ProductionRuns.
- Operators cannot pause ProductionRuns.
- Direct GET access to the pause endpoint returns 403 Forbidden.
- PAUSED ProductionRuns cannot be paused again.
- PLANNED ProductionRuns cannot be paused.
- COMPLETED ProductionRuns cannot be paused.
- CANCELLED ProductionRuns cannot be paused.
- Existing ProductionEntry ACTIVE-status validation remains unchanged.
- Existing DowntimeEvent ACTIVE-status validation remains unchanged.
- No automatic DowntimeEvent creation is introduced.
- No automatic AuditEvent creation is introduced.
- Existing database constraints remain authoritative.
- No database migration is introduced.
- Manual verification uses synthetic manufacturing data.
- 31 ProductionRun interface tests pass.
- 178 Core tests pass.
- Django system checks pass.
- Migration drift check passes.
- Git whitespace validation passes.

## FO-014 Out of Scope

FO-014 does not implement:

- ProductionRun resume workflow
- ProductionRun completion workflow
- ProductionRun cancellation workflow
- ProductionRun editing
- ProductionRun deletion
- pause reason recording
- pause duration tracking
- Operator assignment
- ProductionEntry website workflow
- DowntimeEvent website workflow
- QualityInspection website workflow
- automatic DowntimeEvent creation
- automatic ProductionRun pause from DowntimeEvent creation
- automatic ProductionRun resume from DowntimeEvent closure
- automatic AuditEvent creation for ProductionRun pause actions
- automatic WorkOrder status changes
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 23. FO-015 Current State

## FO-015: Implement Production Run Resume Workflow

FO-015 introduces the ProductionRun resume lifecycle action through the ForgeOps website.

The existing ProductionRun model remains unchanged.

No database migration is required because the existing ProductionRun status set already includes:

```text
PAUSED
ACTIVE
```

## ProductionRun Resume Workflow

An authorised User may resume an existing PAUSED ProductionRun through the ProductionRun detail page.

The workflow is:

```text
PAUSED ProductionRun
        |
        v
Resume Production Run
        |
        v
POST request
        |
        v
Permission validation
        |
        v
ProductionRun state validation
        |
        v
Active-run conflict validation
        |
        v
ACTIVE
```

Resuming a ProductionRun changes:

```text
status -> ACTIVE
```

The existing lifecycle timestamps are preserved.

Successful resume therefore leaves:

```text
started_at -> unchanged
ended_at   -> unchanged
```

Resuming a ProductionRun does not create a new start timestamp and does not end the run.

After a successful resume, the User is redirected back to the ProductionRun detail page.

## Resume Permissions

ProductionRun resume permission is granted to:

- Production Supervisor
- System Administrator
- Django superuser

Operators may inspect ProductionRuns but may not resume them.

Unauthorised resume attempts return:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

FO-015 does not introduce a separate permission system.

## HTTP Method Requirement

ProductionRun resume changes application state and therefore requires:

```text
POST
```

The ProductionRun detail page submits the resume action through a POST form protected by Django CSRF validation.

A direct GET request to the resume endpoint is rejected with:

```text
403 Forbidden
```

The ProductionRun remains unchanged.

## ProductionRun State Requirement

Only ProductionRuns currently in:

```text
PAUSED
```

status may be resumed.

Resume attempts are rejected for ProductionRuns in:

```text
PLANNED
ACTIVE
COMPLETED
CANCELLED
```

Invalid transition attempts return:

```text
403 Forbidden
```

and do not change the ProductionRun state.

## Active ProductionRun Conflict Protection

The existing ProductionRun business rule permits only one ACTIVE ProductionRun for a WorkOrder at a time.

Before resuming a PAUSED ProductionRun, ForgeOps checks whether another ProductionRun for the same WorkOrder is already:

```text
ACTIVE
```

If another ACTIVE ProductionRun exists, the resume request is rejected with:

```text
403 Forbidden
```

The original ProductionRun remains:

```text
PAUSED
```

This application-level validation prevents the existing active-run rule from surfacing as an uncontrolled model or database error during the website workflow.

The existing database constraint remains unchanged and authoritative.

## ProductionRun Detail Integration

For an authorised User, the ProductionRun detail page displays:

```text
Resume Production Run
```

only when the ProductionRun status is:

```text
PAUSED
```

After a successful resume:

- status displays as Active
- the original `started_at` timestamp remains unchanged
- `ended_at` remains unchanged
- the Resume Production Run action disappears
- the Pause Production Run action becomes available
- the Start Production Run action remains unavailable

The ProductionRun detail page therefore reflects the current lifecycle state of the ProductionRun.

## Existing ProductionEntry Behaviour

FO-015 does not introduce new ProductionEntry validation.

The existing ProductionEntry model permits new entries only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a successfully resumed ProductionRun naturally becomes eligible for ProductionEntry records again through the existing model rule.

FO-015 does not duplicate this validation in the resume view.

## Existing DowntimeEvent Behaviour

FO-015 does not introduce new DowntimeEvent validation.

The existing DowntimeEvent model permits new downtime events to be opened only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a successfully resumed ProductionRun naturally becomes eligible for new DowntimeEvent records again through the existing model rule.

FO-015 does not duplicate this validation in the resume view.

## Downtime Independence

FO-015 does not automatically resume a ProductionRun when a DowntimeEvent is closed.

The unresolved business question around:

```text
automatic resume when downtime closes
```

remains unresolved and is not changed by FO-015.

The FO-015 resume workflow is an explicit authorised User action.

## AuditEvent Behaviour

FO-015 does not automatically create an AuditEvent when a ProductionRun is resumed.

The existing FO-010 AuditEvent architecture remains unchanged.

Automatic lifecycle audit logging remains reserved for a future issue that explicitly defines and tests that behaviour.

## Manual FO-015 Verification

FO-015 was manually verified through the ForgeOps website using synthetic manufacturing data.

The primary successful resume test used:

```text
Production Run #3
Work Order: WO-2026-0003
```

Before resume:

```text
Status: PAUSED
Started: 13 Aug 2026, 5:23 p.m.
Ended: Not ended
```

The authorised User was presented with:

```text
Resume Production Run
```

After submitting the resume action:

```text
Status: ACTIVE
Started: 13 Aug 2026, 5:23 p.m.
Ended: Not ended
```

The test demonstrated that:

1. A PAUSED ProductionRun displays the Resume Production Run action to an authorised User.
2. The resume action submits successfully through POST.
3. The ProductionRun changes from PAUSED to ACTIVE.
4. The original `started_at` timestamp remains unchanged.
5. `ended_at` remains unchanged.
6. The Resume Production Run action disappears after the transition.
7. The Pause Production Run action becomes available after the transition.
8. The Start Production Run action remains unavailable.
9. Direct GET access to the resume endpoint returns 403 Forbidden.

Operator permission behaviour was manually verified using:

```text
operator_demo
```

against synthetic:

```text
Production Run #3
```

while the ProductionRun was PAUSED.

The Operator received no Resume Production Run action.

## Manual Active-Run Conflict Verification

FO-015 active-run conflict protection was manually verified using synthetic:

```text
Work Order: WO-2026-0001
```

The test setup was:

```text
Production Run #1 -> PAUSED
Production Run #2 -> ACTIVE
```

Both ProductionRuns belonged to the same WorkOrder.

An authorised User then attempted:

```text
Resume Production Run #1
```

The request returned:

```text
403 Forbidden
```

The blocked ProductionRun remained:

```text
PAUSED
```

while the other ProductionRun remained:

```text
ACTIVE
```

This confirms the resume workflow preserves the one-ACTIVE-run-per-WorkOrder rule.

All records used for manual FO-015 verification were synthetic.

## Automated FO-015 Validation

FO-015 adds eleven ProductionRun resume workflow tests to:

```text
core/tests.py
```

The existing ProductionRun interface test class now contains:

```text
42 tests
```

The dedicated interface test run produced:

```text
Ran 42 tests
OK
```

FO-015 automated tests verify:

- Production Supervisor sees the Resume Production Run action for a PAUSED ProductionRun
- Resume Production Run action is hidden for an ACTIVE ProductionRun
- Resume Production Run action is hidden for a PLANNED ProductionRun
- Operator cannot resume a ProductionRun
- ProductionRun resume requires POST
- Production Supervisor may resume a valid PAUSED ProductionRun
- successful resume changes status to ACTIVE
- successful resume preserves `started_at`
- successful resume preserves `ended_at`
- an ACTIVE ProductionRun cannot be resumed
- a PLANNED ProductionRun cannot be resumed
- a COMPLETED ProductionRun cannot be resumed
- a CANCELLED ProductionRun cannot be resumed
- resume is blocked when another ACTIVE ProductionRun exists for the same WorkOrder
- a blocked resume leaves the original ProductionRun PAUSED
- the conflicting ProductionRun remains ACTIVE

Several related assertions are combined within individual tests.

## Full Core Validation

The full Core test suite after FO-015 produced:

```text
Ran 189 tests
OK
```

FO-015 therefore adds eleven automated tests while preserving the existing 178-test FO-014 baseline.

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-015 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-015 migration is required.

## FO-015 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
docs/database-design.md
```

## FO-015 Acceptance Criteria Verified

- ProductionRun resume workflow is implemented.
- Only authorised Users may resume ProductionRuns.
- Resume operation requires POST.
- Only PAUSED ProductionRuns may be resumed.
- Successful resume changes status to ACTIVE.
- Successful resume preserves the original `started_at`.
- Successful resume preserves `ended_at`.
- Resume action is displayed only for eligible PAUSED ProductionRuns.
- Operators cannot resume ProductionRuns.
- Direct GET access to the resume endpoint returns 403 Forbidden.
- ACTIVE ProductionRuns cannot be resumed.
- PLANNED ProductionRuns cannot be resumed.
- COMPLETED ProductionRuns cannot be resumed.
- CANCELLED ProductionRuns cannot be resumed.
- Resume is blocked when another ACTIVE ProductionRun exists for the same WorkOrder.
- Active-run conflicts return controlled 403 responses.
- Blocked resume leaves the ProductionRun PAUSED.
- Existing FO-013 Start workflow remains functional.
- Existing FO-014 Pause workflow remains functional.
- Existing database constraints remain authoritative.
- Existing ProductionEntry ACTIVE-status validation remains unchanged.
- Existing DowntimeEvent ACTIVE-status validation remains unchanged.
- No automatic DowntimeEvent behaviour is introduced.
- No automatic AuditEvent creation is introduced.
- No automatic WorkOrder status changes are introduced.
- No database migration is introduced.
- Manual verification uses synthetic manufacturing data.
- 42 ProductionRun interface tests pass.
- 189 Core tests pass.
- Django system checks pass.
- Migration drift check passes.
- Git whitespace validation passes.

## FO-015 Out of Scope

FO-015 does not implement:

- ProductionRun completion workflow
- ProductionRun cancellation workflow
- ProductionRun editing
- ProductionRun deletion
- pause reason recording
- pause duration tracking
- Operator assignment
- ProductionEntry website workflow
- DowntimeEvent website workflow
- QualityInspection website workflow
- automatic DowntimeEvent creation
- automatic ProductionRun pause from DowntimeEvent creation
- automatic ProductionRun resume from DowntimeEvent closure
- automatic AuditEvent creation for ProductionRun resume actions
- automatic WorkOrder status changes
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 24. FO-016 Current State

## FO-016: Implement Production Run Completion Workflow

FO-016 introduces the ProductionRun completion lifecycle action through the ForgeOps website.

The existing ProductionRun model remains unchanged.

No database migration is required because the existing ProductionRun status set already includes:

```text
ACTIVE
COMPLETED
```

## ProductionRun Completion Workflow

An authorised User may complete an existing ACTIVE ProductionRun through the ProductionRun detail page.

The workflow is:

```text
ACTIVE ProductionRun
        |
        v
Complete Production Run
        |
        v
POST request
        |
        v
Permission validation
        |
        v
ProductionRun state validation
        |
        v
COMPLETED
```

Completing a ProductionRun changes:

```text
status   -> COMPLETED
ended_at -> current application timestamp
```

The original ProductionRun start timestamp is preserved.

Successful completion therefore leaves:

```text
started_at -> unchanged
ended_at   -> populated
```

After a successful completion, the User is redirected back to the ProductionRun detail page.

## Completion Permissions

ProductionRun completion permission is granted to:

- Production Supervisor
- System Administrator
- Django superuser

Operators may inspect ProductionRuns but may not complete them.

Unauthorised completion attempts return:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

FO-016 does not introduce a separate permission system.

## HTTP Method Requirement

ProductionRun completion changes application state and therefore requires:

```text
POST
```

The ProductionRun detail page submits the completion action through a POST form protected by Django CSRF validation.

A direct GET request to the completion endpoint is rejected with:

```text
403 Forbidden
```

The ProductionRun remains unchanged.

## ProductionRun State Requirement

Only ProductionRuns currently in:

```text
ACTIVE
```

status may be completed.

Completion attempts are rejected for ProductionRuns in:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

Invalid transition attempts return:

```text
403 Forbidden
```

and do not change the ProductionRun state.

A COMPLETED ProductionRun cannot be completed again.

## Completion Timestamp Behaviour

Successful completion automatically records the ProductionRun end timestamp using the current application time.

Conceptually:

```text
ended_at = timezone.now()
```

The existing ProductionRun start timestamp is not replaced.

Successful completion therefore produces:

```text
status     -> COMPLETED
started_at -> unchanged
ended_at   -> populated
```

The existing ProductionRun validation rule remains authoritative:

```text
ended_at >= started_at
```

FO-016 does not duplicate or replace that existing validation.

## ProductionRun Detail Integration

For an authorised User, the ProductionRun detail page displays:

```text
Complete Production Run
```

only when the ProductionRun status is:

```text
ACTIVE
```

An authorised User viewing an ACTIVE ProductionRun may therefore see:

```text
Pause Production Run
Complete Production Run
```

These represent two separate valid lifecycle transitions.

After a successful completion:

- status displays as Completed
- the original `started_at` timestamp remains unchanged
- `ended_at` displays the generated completion timestamp
- the Complete Production Run action disappears
- the Pause Production Run action disappears
- the Resume Production Run action remains unavailable
- the Start Production Run action remains unavailable

A COMPLETED ProductionRun therefore exposes no currently implemented lifecycle action.

## Existing Lifecycle Compatibility

FO-016 preserves all ProductionRun lifecycle behaviour introduced by earlier issues.

FO-013 implements:

```text
PLANNED -> ACTIVE
```

FO-014 implements:

```text
ACTIVE -> PAUSED
```

FO-015 implements:

```text
PAUSED -> ACTIVE
```

FO-016 implements:

```text
ACTIVE -> COMPLETED
```

The implemented lifecycle after FO-016 is:

```text
PLANNED
   |
   | Start
   v
ACTIVE
   |
   |--------------------|
   |                    |
   | Pause              | Complete
   v                    v
PAUSED              COMPLETED
   |
   | Resume
   v
ACTIVE
```

COMPLETED is a terminal state for the lifecycle workflows implemented through FO-016.

FO-016 does not provide a workflow for reopening a COMPLETED ProductionRun.

## Existing ProductionEntry Behaviour

FO-016 does not introduce new ProductionEntry validation.

The existing ProductionEntry model permits new ProductionEntry records only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a COMPLETED ProductionRun naturally rejects new ProductionEntry records through the existing model rule.

FO-016 does not duplicate this validation in the completion view.

FO-016 does not introduce a ProductionEntry website workflow.

## Existing DowntimeEvent Behaviour

FO-016 does not introduce new DowntimeEvent validation.

The existing DowntimeEvent model permits new DowntimeEvents to be opened only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a COMPLETED ProductionRun naturally rejects new DowntimeEvent creation through the existing model rule.

FO-016 does not duplicate this validation in the completion view.

## Downtime Independence

FO-016 does not automatically:

- create a DowntimeEvent
- close an existing DowntimeEvent
- pause a ProductionRun when downtime opens
- resume a ProductionRun when downtime closes

The unresolved business questions around automatic ProductionRun lifecycle changes from downtime remain outside FO-016.

FO-016 also does not introduce a new rule requiring all DowntimeEvents to be closed before completion.

Any future rule linking open DowntimeEvents to ProductionRun completion must be implemented through a separate roadmap issue.

## QualityInspection Behaviour

FO-016 does not introduce QualityInspection completion requirements.

Existing QualityInspection model validation remains unchanged.

ProductionRun completion through FO-016 does not require:

- all QualityInspection records to be completed
- all QualityInspection records to be PASSED
- absence of PENDING QualityInspection records
- quality approval before ProductionRun completion

The existing documentation already identifies ProductionRun quality-completion requirements as unresolved.

FO-016 therefore does not silently introduce a new quality gate.

Any future rule connecting QualityInspection state to ProductionRun completion must be explicitly defined and tested through a separate roadmap issue.

## WorkOrder Behaviour

FO-016 does not automatically modify the status of the associated WorkOrder.

Completing a ProductionRun does not automatically change the WorkOrder to:

```text
COMPLETED
```

or any other WorkOrder state.

Automatic WorkOrder lifecycle behaviour remains reserved for a future roadmap issue.

## AuditEvent Behaviour

FO-016 does not automatically create an AuditEvent when a ProductionRun is completed.

The existing FO-010 AuditEvent architecture remains unchanged.

Automatic lifecycle audit logging remains reserved for a future issue that explicitly defines and tests that behaviour.

## Manual FO-016 Verification

FO-016 was manually verified through the ForgeOps website using synthetic manufacturing data.

The primary manual completion test used:

```text
Production Run #2
Work Order: WO-2026-0001
Production Line: LINE-A01 - Line A
Shift: Night Shift
```

Before completion:

```text
Status: ACTIVE
Started: 14 Aug 2026, 4:30 p.m.
Ended: Not ended
```

The authorised User was presented with:

```text
Pause Production Run
Complete Production Run
```

After submitting the completion action:

```text
Status: COMPLETED
Started: 14 Aug 2026, 4:30 p.m.
Ended: 14 Aug 2026, 5:54 p.m.
```

The manual test demonstrated that:

- An ACTIVE ProductionRun displays the Complete Production Run action to an authorised User.
- The completion action submits successfully through POST.
- The ProductionRun changes from ACTIVE to COMPLETED.
- The original `started_at` timestamp remains unchanged.
- `ended_at` is populated automatically.
- The generated `ended_at` timestamp is later than the existing `started_at` timestamp.
- The Complete Production Run action disappears after successful completion.
- The Pause Production Run action disappears after successful completion.
- The Resume Production Run action is unavailable for the COMPLETED run.
- The Start Production Run action is unavailable for the COMPLETED run.
- Direct GET access to the completion endpoint returns 403 Forbidden.

Operator permission behaviour was manually verified using:

```text
operator_demo
```

against an ACTIVE synthetic ProductionRun.

The Operator could inspect the ProductionRun but received no:

```text
Complete Production Run
```

action.

Direct browser access to:

```text
/production-runs/2/complete/
```

using GET returned:

```text
403 Forbidden
```

All records used for manual FO-016 verification were synthetic.

## Automated FO-016 Validation

FO-016 adds ten ProductionRun completion workflow tests to:

```text
core/tests.py
```

The existing ProductionRun interface test class now contains:

```text
52 tests
```

The dedicated interface test run produced:

```text
Ran 52 tests
OK
```

FO-016 automated tests verify:

- Production Supervisor sees the Complete Production Run action for an ACTIVE ProductionRun
- Complete Production Run action is hidden for a PLANNED ProductionRun
- Complete Production Run action is hidden for a PAUSED ProductionRun
- Operator cannot complete a ProductionRun
- ProductionRun completion requires POST
- Production Supervisor may complete a valid ACTIVE ProductionRun
- successful completion changes status to COMPLETED
- successful completion preserves `started_at`
- successful completion populates `ended_at`
- generated `ended_at` is not earlier than `started_at`
- a PLANNED ProductionRun cannot be completed
- a PAUSED ProductionRun cannot be completed
- a COMPLETED ProductionRun cannot be completed again
- a CANCELLED ProductionRun cannot be completed
- rejected completion attempts preserve the existing ProductionRun state

Several related assertions are combined within individual tests.

## Full Core Validation

The full Core test suite after FO-016 produced:

```text
Ran 199 tests
OK
```

FO-016 therefore adds ten automated tests while preserving the existing 189-test FO-015 baseline.

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-016 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-016 migration is required.

## FO-016 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
docs/database-design.md
```

## FO-016 Acceptance Criteria Verified

- ProductionRun completion workflow is implemented.
- The valid completion transition is ACTIVE to COMPLETED.
- Only authorised Users may complete ProductionRuns.
- Production Supervisor completion permission is implemented.
- System Administrator completion permission is implemented in permission logic.
- Django superuser completion permission is implemented.
- Operators cannot complete ProductionRuns.
- Completion requires POST.
- Direct GET completion requests return 403 Forbidden.
- Only ACTIVE ProductionRuns may be completed.
- PLANNED ProductionRuns cannot be completed.
- PAUSED ProductionRuns cannot be completed.
- COMPLETED ProductionRuns cannot be completed again.
- CANCELLED ProductionRuns cannot be completed.
- Successful completion changes status to COMPLETED.
- Successful completion preserves the original `started_at`.
- Successful completion automatically records `ended_at`.
- Completion timestamp ordering remains protected by existing validation.
- Complete Production Run appears only for eligible ACTIVE ProductionRuns.
- Complete Production Run disappears after successful completion.
- Pause Production Run disappears after successful completion.
- Start Production Run is unavailable for COMPLETED ProductionRuns.
- Resume Production Run is unavailable for COMPLETED ProductionRuns.
- Existing FO-013 Start workflow remains functional.
- Existing FO-014 Pause workflow remains functional.
- Existing FO-015 Resume workflow remains functional.
- Existing ProductionEntry ACTIVE-status validation remains unchanged.
- Existing DowntimeEvent ACTIVE-status validation remains unchanged.
- Existing QualityInspection validation remains unchanged.
- QualityInspection records do not currently block ProductionRun completion.
- No automatic DowntimeEvent behaviour is introduced.
- No automatic AuditEvent creation is introduced.
- No automatic WorkOrder status changes are introduced.
- Existing database constraints remain authoritative.
- No database migration is introduced.
- Manual verification uses synthetic manufacturing data.
- 52 ProductionRun interface tests pass.
- 199 Core tests pass.
- Django system checks pass.
- Migration drift check passes.
- Git whitespace validation passes.

## FO-016 Out of Scope

FO-016 does not implement:

- ProductionRun cancellation workflow
- ProductionRun editing
- ProductionRun deletion
- reopening a COMPLETED ProductionRun
- completion reason recording
- completion comments workflow beyond existing ProductionRun notes
- electronic signatures
- completion approval workflow
- Operator assignment
- pause reason recording
- pause duration tracking
- ProductionEntry website workflow
- DowntimeEvent website workflow
- QualityInspection website workflow
- mandatory PASSED QualityInspection before ProductionRun completion
- mandatory completion of all QualityInspection records before ProductionRun completion
- blocking ProductionRun completion because of an open DowntimeEvent
- automatic DowntimeEvent creation
- automatic DowntimeEvent closure
- automatic ProductionRun pause from DowntimeEvent creation
- automatic ProductionRun resume from DowntimeEvent closure
- automatic AuditEvent creation for ProductionRun completion actions
- automatic WorkOrder status changes
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 25. FO-017 Current State

## FO-017: Implement Production Run Cancellation Workflow

FO-017 introduces the ProductionRun cancellation lifecycle action through the ForgeOps website.

The existing ProductionRun model remains unchanged.

No database migration is required because the existing ProductionRun status set already includes:

```text
CANCELLED
```

## ProductionRun Cancellation Workflow

An authorised User may cancel an eligible ProductionRun through the ProductionRun detail page.

The workflow is:

```text
PLANNED / ACTIVE / PAUSED ProductionRun
        |
        v
Cancel Production Run
        |
        v
POST request
        |
        v
Permission validation
        |
        v
ProductionRun state validation
        |
        v
CANCELLED
```

Cancellation is permitted from:

```text
PLANNED
ACTIVE
PAUSED
```

Cancellation is not permitted from:

```text
COMPLETED
CANCELLED
```

After successful cancellation, the User is redirected back to the ProductionRun detail page.

## Cancellation Permissions

ProductionRun cancellation permission is granted to:

- Production Supervisor
- System Administrator
- Django superuser

Operators may inspect ProductionRuns but may not cancel them.

Unauthorised cancellation attempts return:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

FO-017 does not introduce a separate permission system.

## HTTP Method Requirement

ProductionRun cancellation changes application state and therefore requires:

```text
POST
```

The ProductionRun detail page submits the cancellation action through a POST form protected by Django CSRF validation.

A direct GET request to the cancellation endpoint is rejected with:

```text
403 Forbidden
```

The ProductionRun remains unchanged.

## ProductionRun State Requirement

Cancellation is allowed only when the ProductionRun currently has status:

```text
PLANNED
ACTIVE
PAUSED
```

Cancellation attempts are rejected for:

```text
COMPLETED
CANCELLED
```

Invalid transition attempts return:

```text
403 Forbidden
```

and do not modify the existing ProductionRun state.

A CANCELLED ProductionRun cannot be cancelled again.

A COMPLETED ProductionRun cannot later be cancelled through FO-017.

## PLANNED Cancellation Behaviour

Cancelling a PLANNED ProductionRun changes:

```text
status -> CANCELLED
```

A PLANNED ProductionRun has not started execution.

Therefore cancellation leaves:

```text
started_at -> None
ended_at   -> None
```

FO-017 does not create artificial execution timestamps for a ProductionRun that never started.

Conceptually:

```text
PLANNED
   |
   | Cancel
   v
CANCELLED

started_at = None
ended_at   = None
```

## ACTIVE Cancellation Behaviour

Cancelling an ACTIVE ProductionRun changes:

```text
status   -> CANCELLED
ended_at -> current application timestamp
```

The original start timestamp is preserved.

Successful ACTIVE cancellation therefore leaves:

```text
started_at -> unchanged
ended_at   -> populated
```

Conceptually:

```text
ACTIVE
   |
   | Cancel
   v
CANCELLED

started_at = original start timestamp
ended_at   = cancellation timestamp
```

The existing ProductionRun timestamp validation remains authoritative:

```text
ended_at >= started_at
```

## PAUSED Cancellation Behaviour

A PAUSED ProductionRun represents manufacturing execution that previously started but is temporarily suspended.

Cancelling a PAUSED ProductionRun therefore changes:

```text
status   -> CANCELLED
ended_at -> current application timestamp
```

The original start timestamp remains unchanged.

Successful PAUSED cancellation therefore leaves:

```text
started_at -> unchanged
ended_at   -> populated
```

Conceptually:

```text
PAUSED
   |
   | Cancel
   v
CANCELLED

started_at = original start timestamp
ended_at   = cancellation timestamp
```

## Terminal Cancellation State

After cancellation, the ProductionRun enters:

```text
CANCELLED
```

CANCELLED is treated as a terminal state by the currently implemented ProductionRun website lifecycle.

A CANCELLED ProductionRun cannot currently be:

- started
- paused
- resumed
- completed
- cancelled again

FO-017 does not implement reopening a CANCELLED ProductionRun.

## ProductionRun Detail Integration

For an authorised User, the ProductionRun detail page displays:

```text
Cancel Production Run
```

when the ProductionRun status is:

```text
PLANNED
ACTIVE
PAUSED
```

The cancellation action is not displayed when status is:

```text
COMPLETED
CANCELLED
```

The other lifecycle actions continue to follow their existing state requirements.

For PLANNED:

```text
Start Production Run
Cancel Production Run
```

For ACTIVE:

```text
Pause Production Run
Complete Production Run
Cancel Production Run
```

For PAUSED:

```text
Resume Production Run
Cancel Production Run
```

For COMPLETED:

```text
No currently implemented lifecycle action
```

For CANCELLED:

```text
No currently implemented lifecycle action
```

## Existing Lifecycle Compatibility

FO-017 preserves the ProductionRun lifecycle behaviour introduced by earlier issues.

FO-013 implements:

```text
PLANNED -> ACTIVE
```

FO-014 implements:

```text
ACTIVE -> PAUSED
```

FO-015 implements:

```text
PAUSED -> ACTIVE
```

FO-016 implements:

```text
ACTIVE -> COMPLETED
```

FO-017 adds:

```text
PLANNED -> CANCELLED
ACTIVE  -> CANCELLED
PAUSED  -> CANCELLED
```

The implemented lifecycle after FO-017 is therefore:

```text
                    Cancel
              ┌───────────────► CANCELLED
              │
           PLANNED
              │
              │ Start
              ▼
           ACTIVE ─────────────► CANCELLED
              │     Cancel
              │
        ┌─────┴─────┐
        │           │
      Pause      Complete
        │           │
        ▼           ▼
     PAUSED      COMPLETED
        │
        │ Resume
        └────────► ACTIVE

PAUSED ─────────────► CANCELLED
          Cancel
```

COMPLETED and CANCELLED are terminal states for the ProductionRun lifecycle currently implemented.

## Existing ProductionEntry Behaviour

FO-017 does not change ProductionEntry validation.

The existing ProductionEntry model permits new ProductionEntry records only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a CANCELLED ProductionRun naturally rejects new ProductionEntry records through existing model validation.

FO-017 does not introduce a ProductionEntry website workflow.

## Existing DowntimeEvent Behaviour

FO-017 does not change DowntimeEvent validation.

The existing DowntimeEvent model permits new DowntimeEvents to be opened only against ProductionRuns with:

```text
ACTIVE
```

status.

Therefore a CANCELLED ProductionRun naturally rejects new DowntimeEvent creation.

FO-017 does not automatically close an existing open DowntimeEvent during cancellation.

FO-017 also does not block ProductionRun cancellation because an open DowntimeEvent exists.

Any future relationship between ProductionRun cancellation and DowntimeEvent closure must be explicitly defined through a later roadmap issue.

## QualityInspection Behaviour

FO-017 does not modify QualityInspection behaviour.

Existing QualityInspection records remain associated with the ProductionRun.

Cancellation does not:

- delete QualityInspection records
- automatically complete pending QualityInspections
- automatically pass or fail QualityInspections
- require QualityInspection approval
- create new QualityInspection records

QualityInspection workflow behaviour remains independent.

## WorkOrder Behaviour

FO-017 does not automatically modify the associated WorkOrder.

Cancelling a ProductionRun does not automatically change the WorkOrder to:

```text
CANCELLED
```

or any other WorkOrder state.

A WorkOrder may contain multiple ProductionRuns, so ProductionRun cancellation and WorkOrder cancellation are deliberately treated as separate concepts.

Automatic WorkOrder lifecycle changes remain reserved for a future issue.

## AuditEvent Behaviour

FO-017 does not automatically create an AuditEvent when a ProductionRun is cancelled.

The existing FO-010 AuditEvent architecture remains unchanged.

Automatic lifecycle audit logging remains reserved for a future issue that explicitly defines and tests that behaviour.

## Manual FO-017 Verification

FO-017 was manually verified through the ForgeOps website using synthetic manufacturing data.

### PLANNED Cancellation

A synthetic ProductionRun was created for:

```text
Work Order: WO-2026-0003
Product: PRD-1001 - Synthetic Medical Device Assembly
Production Line: LINE-A01 - Line A
Shift: Night Shift
```

The new ProductionRun was:

```text
Production Run #4
Status: PLANNED
Started: Not started
Ended: Not ended
```

The notes were:

```text
Synthetic FO-017 PLANNED cancellation workflow test.
```

The authorised User was presented with:

```text
Start Production Run
Cancel Production Run
```

After cancellation:

```text
Production Run #4
Status: CANCELLED
Started: Not started
Ended: Not ended
```

The lifecycle actions disappeared.

This confirmed that cancelling an unstarted PLANNED ProductionRun does not fabricate start or end timestamps.

### ACTIVE Cancellation

A second synthetic ProductionRun was created and started:

```text
Production Run #5
Work Order: WO-2026-0003
Status: ACTIVE
```

The notes were:

```text
Synthetic FO-017 ACTIVE cancellation workflow test.
```

Before cancellation, the page displayed:

```text
Pause Production Run
Complete Production Run
Cancel Production Run
```

The ProductionRun contained an existing start timestamp.

After cancellation:

```text
Status: CANCELLED
Started: original start timestamp preserved
Ended: cancellation timestamp populated
```

All lifecycle actions disappeared.

This confirmed that ACTIVE cancellation preserves manufacturing start history and records the point at which execution was cancelled.

### PAUSED Cancellation

An existing synthetic PAUSED ProductionRun was also cancelled.

Before cancellation:

```text
Status: PAUSED
Started: populated
Ended: Not ended
```

The authorised User was presented with:

```text
Resume Production Run
Cancel Production Run
```

After cancellation:

```text
Status: CANCELLED
Started: original start timestamp preserved
Ended: cancellation timestamp populated
```

### Terminal-State Verification

The existing synthetic ProductionRuns were manually inspected after cancellation.

CANCELLED ProductionRuns displayed no:

```text
Start Production Run
Pause Production Run
Resume Production Run
Complete Production Run
Cancel Production Run
```

actions.

A previously COMPLETED ProductionRun also displayed no cancellation action.

### Direct URL Verification

Direct GET access to the cancellation endpoint was manually attempted.

Example:

```text
/production-runs/3/cancel/
```

The request returned:

```text
403 Forbidden
```

This confirmed that ProductionRun cancellation cannot be triggered through ordinary GET navigation.

All records used for FO-017 manual verification were synthetic.

## Automated FO-017 Validation

FO-017 extends the existing ProductionRun interface tests in:

```text
core/tests.py
```

The ProductionRun interface test class after FO-017 contains:

```text
64 tests
```

The dedicated interface test run produced:

```text
Ran 64 tests
OK
```

FO-017 automated tests verify:

- Production Supervisor sees Cancel Production Run for a PLANNED ProductionRun
- Production Supervisor sees Cancel Production Run for an ACTIVE ProductionRun
- Production Supervisor sees Cancel Production Run for a PAUSED ProductionRun
- Operator does not receive ProductionRun cancellation permission
- cancellation requires POST
- Production Supervisor can cancel a PLANNED ProductionRun
- PLANNED cancellation changes status to CANCELLED
- PLANNED cancellation preserves an empty `started_at`
- PLANNED cancellation preserves an empty `ended_at`
- Production Supervisor can cancel an ACTIVE ProductionRun
- ACTIVE cancellation changes status to CANCELLED
- ACTIVE cancellation preserves the original `started_at`
- ACTIVE cancellation populates `ended_at`
- Production Supervisor can cancel a PAUSED ProductionRun
- PAUSED cancellation changes status to CANCELLED
- PAUSED cancellation preserves the original `started_at`
- PAUSED cancellation populates `ended_at`
- COMPLETED ProductionRuns cannot be cancelled
- CANCELLED ProductionRuns cannot be cancelled again
- rejected cancellation attempts preserve existing ProductionRun state

## Full Core Validation

The full Core test suite after FO-017 produced:

```text
Ran 211 tests in 20.685s
OK
```

FO-017 therefore extends the previous FO-016 baseline of:

```text
199 tests
```

to:

```text
211 tests
```

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-017 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-017 migration is required.

## FO-017 Files Updated

```text
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
docs/database-design.md
```

## FO-017 Acceptance Criteria Verified

- ProductionRun cancellation workflow is implemented.
- Cancellation permission is role controlled.
- Production Supervisor cancellation permission is implemented.
- System Administrator cancellation permission is implemented in permission logic.
- Django superuser cancellation permission is implemented.
- Operators cannot cancel ProductionRuns.
- Cancellation requires POST.
- Direct GET cancellation requests return 403 Forbidden.
- PLANNED ProductionRuns may be cancelled.
- ACTIVE ProductionRuns may be cancelled.
- PAUSED ProductionRuns may be cancelled.
- COMPLETED ProductionRuns cannot be cancelled.
- CANCELLED ProductionRuns cannot be cancelled again.
- PLANNED cancellation changes status to CANCELLED.
- PLANNED cancellation leaves `started_at` empty.
- PLANNED cancellation leaves `ended_at` empty.
- ACTIVE cancellation changes status to CANCELLED.
- ACTIVE cancellation preserves the original `started_at`.
- ACTIVE cancellation automatically records `ended_at`.
- PAUSED cancellation changes status to CANCELLED.
- PAUSED cancellation preserves the original `started_at`.
- PAUSED cancellation automatically records `ended_at`.
- Existing timestamp ordering validation remains authoritative.
- Cancel Production Run appears only for eligible PLANNED, ACTIVE and PAUSED ProductionRuns.
- Cancel Production Run is unavailable for COMPLETED ProductionRuns.
- Cancel Production Run is unavailable for CANCELLED ProductionRuns.
- CANCELLED ProductionRuns expose no implemented lifecycle actions.
- Existing FO-013 Start workflow remains functional.
- Existing FO-014 Pause workflow remains functional.
- Existing FO-015 Resume workflow remains functional.
- Existing FO-016 Completion workflow remains functional.
- Existing ProductionEntry ACTIVE-status validation remains unchanged.
- Existing DowntimeEvent ACTIVE-status validation remains unchanged.
- Existing QualityInspection validation remains unchanged.
- No automatic DowntimeEvent behaviour is introduced.
- No automatic AuditEvent creation is introduced.
- No automatic WorkOrder status changes are introduced.
- Existing database constraints remain authoritative.
- No database migration is introduced.
- Manual verification uses synthetic manufacturing data.
- 64 ProductionRun interface tests pass.
- 211 Core tests pass.
- Django system checks pass.
- Migration drift check passes.
- Git whitespace validation passes.

## FO-017 Out of Scope

FO-017 does not implement:

- ProductionRun reopening after cancellation
- ProductionRun editing
- ProductionRun deletion
- cancellation reason recording
- cancellation comments workflow beyond existing ProductionRun notes
- cancellation approval workflow
- electronic signatures
- Operator assignment
- pause reason recording
- pause duration tracking
- ProductionEntry website workflow
- DowntimeEvent website workflow
- QualityInspection website workflow
- automatic closure of open DowntimeEvents during cancellation
- blocking cancellation because of open DowntimeEvents
- automatic ProductionRun pause from DowntimeEvent creation
- automatic ProductionRun resume from DowntimeEvent closure
- automatic AuditEvent creation for ProductionRun cancellation actions
- automatic WorkOrder status changes
- WorkOrder cancellation propagation
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 26. FO-018 Current State

## FO-018: Implement ProductionEntry Website Workflow

FO-018 introduces the first website workflow for recording manufacturing output against an existing ACTIVE ProductionRun.

The existing ProductionEntry model remains unchanged.

No database migration is required because FO-018 uses the existing ProductionEntry schema introduced in:

```text
0005_create_production_entries
```

The website workflow allows authorised Users to record:

```text
good_quantity
rejected_quantity
```

against an ACTIVE ProductionRun.

The ProductionRun relationship and authenticated User are assigned automatically by the server.

## ProductionEntry Website Workflow

The workflow is:

```text
ACTIVE ProductionRun
        |
        v
Record Production Entry
        |
        v
ProductionEntry form
        |
        v
Quantity validation
        |
        v
ProductionRun state validation
        |
        v
ProductionEntry created
        |
        v
recorded_by assigned automatically
        |
        v
Redirect to ProductionRun detail page
        |
        v
ProductionRun totals recalculated from related entries
```

The User does not manually select the ProductionRun.

The ProductionRun is determined from the URL:

```text
/production-runs/<production_run_pk>/entries/new/
```

The authenticated User is assigned automatically to:

```text
recorded_by
```

This prevents a User from selecting another User as the ProductionEntry recorder through the website form.

## ProductionEntry Form

FO-018 introduces a dedicated ModelForm for ProductionEntry creation.

The website form exposes only:

```text
good_quantity
rejected_quantity
```

The following ProductionEntry fields are not directly editable through the form:

```text
production_run
recorded_by
recorded_at
```

The ProductionRun is assigned by the view.

The authenticated User is assigned to `recorded_by`.

`recorded_at` continues to be populated automatically by the existing model field.

## Quantity Validation

The existing ProductionEntry validation remains authoritative.

A valid ProductionEntry must contain at least one recorded unit.

Therefore:

```text
good_quantity = 0
rejected_quantity = 0
```

is invalid.

The ProductionEntry model continues to enforce:

```text
good_quantity >= 0
rejected_quantity >= 0
```

and:

```text
good_quantity > 0
```

OR

```text
rejected_quantity > 0
```

The existing database constraint remains:

```text
production_entry_quantity_required
```

Negative quantities remain invalid.

FO-018 does not modify these existing model or database rules.

## ProductionRun State Protection

ProductionEntry creation is permitted only when the related ProductionRun has status:

```text
ACTIVE
```

The following ProductionRun states cannot accept new ProductionEntries:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

Direct access to the ProductionEntry creation endpoint for an ineligible ProductionRun returns:

```text
403 Forbidden
```

This means hiding the Record Production Entry button is not the only protection.

The server-side view independently verifies the current ProductionRun state before allowing the form to be used.

## ProductionEntry Permissions

FO-018 permits ProductionEntry recording for authenticated manufacturing Users allowed by the website workflow.

Manual and automated verification confirm that an Operator can record ProductionEntries against an ACTIVE ProductionRun.

ProductionEntry creation still requires authentication.

Unauthenticated access redirects to the login workflow.

The current FO-018 scope does not introduce a separate ProductionEntry permission model or Django permission object.

## ProductionRun Detail Integration

The ProductionRun detail page now displays a:

```text
Record Production Entry
```

action when the ProductionRun is ACTIVE.

The action is not displayed when the ProductionRun is:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

The ProductionRun detail page also contains a Production Entries section.

When no ProductionEntries exist, the page displays:

```text
No production entries recorded.
```

When entries exist, the page displays each related ProductionEntry including:

```text
Good Quantity
Rejected Quantity
Recorded By
Recorded At
```

Existing ProductionEntries remain visible when the ProductionRun later moves out of ACTIVE status.

FO-018 does not delete or hide historical ProductionEntries when a ProductionRun is paused, completed or cancelled.

## ProductionEntry Ordering

The existing ProductionEntry ordering remains:

```text
-recorded_at
-id
```

This causes the newest ProductionEntry to be displayed first.

FO-018 preserves this model behaviour.

## ProductionRun Aggregation

The existing ProductionRun calculated values automatically aggregate related ProductionEntries.

FO-018 exposes this existing behaviour through the website.

The ProductionRun detail page continues to display:

```text
Good Quantity
Rejected Quantity
Total Recorded
Completion
```

These values are calculated from related ProductionEntry records.

FO-018 does not store duplicated aggregate quantity fields on ProductionRun.

The related ProductionEntry records remain the source of truth.

## Manual FO-018 Verification

Manual verification used synthetic manufacturing data only.

The primary manual verification used:

```text
Production Run #6
Work Order: WO-2026-0003
Product: PRD-1001 - Synthetic Medical Device Assembly
Production Line: LINE-A01 - Line A
Shift: Night Shift
```

Production Run #6 was initially created as:

```text
PLANNED
```

and then started through the existing ProductionRun start workflow.

After starting, the ProductionRun became:

```text
ACTIVE
```

The ProductionRun detail page then displayed:

```text
Pause Production Run
Complete Production Run
Cancel Production Run
Record Production Entry
```

The Production Entries section initially displayed:

```text
No production entries recorded.
```

## First ProductionEntry Verification

The first synthetic ProductionEntry recorded:

```text
Good Quantity: 48
Rejected Quantity: 2
```

The ProductionRun totals then displayed:

```text
Good Quantity: 48
Rejected Quantity: 2
Total Recorded: 50
Completion: 10.0%
```

The Production Entries section displayed the new entry with:

```text
Good Quantity: 48
Rejected Quantity: 2
Recorded By: admin
```

This confirmed:

- ProductionEntry creation succeeds against an ACTIVE ProductionRun
- the ProductionEntry is associated with the requested ProductionRun
- `recorded_by` is assigned automatically
- ProductionRun aggregate values update correctly
- the new ProductionEntry is displayed on the ProductionRun detail page

## Multiple ProductionEntry Verification

A second synthetic ProductionEntry recorded:

```text
Good Quantity: 88
Rejected Quantity: 12
```

The two ProductionEntries therefore contained:

```text
Entry 1:
Good Quantity: 48
Rejected Quantity: 2
Total: 50

Entry 2:
Good Quantity: 88
Rejected Quantity: 12
Total: 100
```

The ProductionRun aggregate values became:

```text
Good Quantity: 136
Rejected Quantity: 14
Total Recorded: 150
Completion: 30.0%
```

The associated WorkOrder planned quantity was:

```text
500
```

Therefore:

```text
150 / 500 * 100 = 30.0%
```

This confirmed the existing ProductionRun aggregation behaviour remains correct when multiple ProductionEntries are recorded.

The newest ProductionEntry appeared first in the Production Entries section.

## Invalid Quantity Manual Verification

FO-018 manually verified rejection of:

```text
Good Quantity: 0
Rejected Quantity: 0
```

The invalid submission did not create a ProductionEntry.

The existing model validation remained authoritative.

The ProductionRun totals remained unchanged.

## PAUSED ProductionRun Manual Verification

Production Run #6 was then paused through the existing FO-014 workflow.

Its status became:

```text
PAUSED
```

The Record Production Entry action disappeared from the ProductionRun detail page.

Existing ProductionEntries remained visible.

The aggregate values remained:

```text
Good Quantity: 136
Rejected Quantity: 14
Total Recorded: 150
Completion: 30.0%
```

Direct access to:

```text
/production-runs/6/entries/new/
```

returned:

```text
403 Forbidden
```

This confirms that ProductionEntry creation is protected at the server level and cannot be bypassed by manually entering the endpoint URL.

All manual FO-018 records were synthetic.

## Automated FO-018 Validation

FO-018 introduces a dedicated:

```text
ProductionEntryInterfaceTests
```

test class in:

```text
core/tests.py
```

The dedicated FO-018 test run produced:

```text
Found 25 test(s).
Ran 25 tests
OK
```

The automated FO-018 tests verify:

- ProductionEntry creation requires authentication
- Operator may access the ProductionEntry creation page for an ACTIVE ProductionRun
- Production Supervisor may access the ProductionEntry creation page for an ACTIVE ProductionRun
- Record Production Entry is displayed for an ACTIVE ProductionRun
- Record Production Entry is hidden for a PLANNED ProductionRun
- Record Production Entry is hidden for a PAUSED ProductionRun
- Record Production Entry is hidden for a COMPLETED ProductionRun
- Record Production Entry is hidden for a CANCELLED ProductionRun
- an Operator may create a valid ProductionEntry
- a created ProductionEntry belongs to the requested ProductionRun
- `recorded_by` is assigned to the authenticated User
- zero good and zero rejected quantity is rejected
- negative good quantity is rejected
- negative rejected quantity is rejected
- PLANNED ProductionRuns cannot accept ProductionEntries
- PAUSED ProductionRuns cannot accept ProductionEntries
- COMPLETED ProductionRuns cannot accept ProductionEntries
- CANCELLED ProductionRuns cannot accept ProductionEntries
- multiple entries aggregate good quantity correctly
- multiple entries aggregate rejected quantity correctly
- multiple entries aggregate total recorded quantity correctly
- multiple entries aggregate completion percentage correctly
- ProductionRun detail displays ProductionEntries
- ProductionRun detail displays the empty ProductionEntry state
- ProductionEntries use newest-first ordering

## Full Core Validation

The complete Core regression suite after FO-018 produced:

```text
Ran 236 tests in 20.972s
OK
```

FO-018 therefore adds:

```text
25 tests
```

to the previous FO-017 baseline of:

```text
211 tests
```

resulting in:

```text
236 Core tests
```

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

Python syntax validation for the expanded test file also passed using:

```text
python -m py_compile core/tests.py
```

## Migration Verification

FO-018 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-018 migration is required.

The ProductionEntry schema introduced in migration:

```text
0005_create_production_entries
```

remains authoritative.

## FO-018 Files Updated

FO-018 updates:

```text
core/forms.py
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
core/templates/core/production_entry_form.html
docs/database-design.md
```

## FO-018 Acceptance Criteria Verified

- ProductionEntry website workflow is implemented.
- ProductionEntry creation requires authentication.
- ProductionEntry creation is associated with a specific ProductionRun.
- ProductionRun is determined by the endpoint rather than editable form input.
- `recorded_by` is assigned automatically from the authenticated User.
- `recorded_at` continues to be populated automatically.
- ProductionEntry form exposes good quantity.
- ProductionEntry form exposes rejected quantity.
- ProductionEntry form does not expose `production_run`.
- ProductionEntry form does not expose `recorded_by`.
- ProductionEntry form does not expose `recorded_at`.
- ProductionEntry creation is allowed for ACTIVE ProductionRuns.
- PLANNED ProductionRuns cannot accept ProductionEntries.
- PAUSED ProductionRuns cannot accept ProductionEntries.
- COMPLETED ProductionRuns cannot accept ProductionEntries.
- CANCELLED ProductionRuns cannot accept ProductionEntries.
- Direct access against an ineligible ProductionRun returns 403 Forbidden.
- Record Production Entry action is displayed for ACTIVE ProductionRuns.
- Record Production Entry action is hidden for PLANNED ProductionRuns.
- Record Production Entry action is hidden for PAUSED ProductionRuns.
- Record Production Entry action is hidden for COMPLETED ProductionRuns.
- Record Production Entry action is hidden for CANCELLED ProductionRuns.
- Existing ProductionEntries remain visible after the run leaves ACTIVE status.
- zero good and zero rejected quantity is rejected.
- negative good quantity is rejected.
- negative rejected quantity is rejected.
- ProductionEntry model validation remains authoritative.
- ProductionEntry database constraints remain authoritative.
- related ProductionEntries are displayed on the ProductionRun detail page.
- an empty ProductionEntry state is displayed when no entries exist.
- newest ProductionEntry is displayed first.
- ProductionRun good quantity aggregation remains correct.
- ProductionRun rejected quantity aggregation remains correct.
- ProductionRun total recorded quantity aggregation remains correct.
- ProductionRun completion percentage aggregation remains correct.
- multiple ProductionEntries are supported.
- existing ProductionRun Start workflow remains functional.
- existing ProductionRun Pause workflow remains functional.
- existing ProductionRun Resume workflow remains functional.
- existing ProductionRun Completion workflow remains functional.
- existing ProductionRun Cancellation workflow remains functional.
- no automatic ProductionRun status transition occurs from ProductionEntry creation.
- no automatic WorkOrder status transition occurs from ProductionEntry creation.
- no automatic AuditEvent is created.
- no DowntimeEvent behaviour is changed.
- no QualityInspection behaviour is changed.
- no database migration is introduced.
- all manual test data is synthetic.
- 25 dedicated FO-018 tests pass.
- 236 Core tests pass.
- Django system checks pass.
- Python syntax validation passes.
- migration drift check passes.
- Git whitespace validation passes.

## FO-018 Out of Scope

FO-018 does not implement:

- ProductionEntry editing
- ProductionEntry deletion
- ProductionEntry correction workflow
- ProductionEntry approval workflow
- ProductionEntry rejection workflow
- ProductionEntry electronic signatures
- ProductionEntry batch entry
- ProductionEntry bulk import
- ProductionEntry CSV import
- ProductionEntry spreadsheet import
- ProductionEntry barcode entry
- ProductionEntry machine-generated records
- ProductionEntry MES integration
- ProductionEntry API endpoints
- ProductionEntry comments beyond the existing model design
- automatic ProductionRun completion based on recorded quantity
- automatic ProductionRun pause based on ProductionEntry creation
- automatic ProductionRun resume based on ProductionEntry creation
- automatic WorkOrder status changes
- automatic WorkOrder completion
- automatic AuditEvent creation
- DowntimeEvent website workflow
- QualityInspection website workflow
- mandatory QualityInspection before recording production
- operator assignment to ProductionRun
- production lot or batch tracking
- serial number tracking
- scrap reason capture
- rejected quantity reason capture
- rework tracking
- material consumption tracking
- machine integration
- MES integration
- REST API endpoints
- dashboard analytics
- production scheduling optimisation
- real manufacturing data

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.

# 27. FO-019 Current State

## FO-019: Implement DowntimeEvent Website Workflow

FO-019 introduces the first website workflow for opening, displaying and closing DowntimeEvent records against an existing ACTIVE ProductionRun.

The existing DowntimeEvent model remains unchanged.

No database migration is required because FO-019 uses the existing DowntimeEvent schema introduced in:

```text
0006_downtimeevent
```

The website workflow allows authorised Users to:

- open a DowntimeEvent against an ACTIVE ProductionRun
- select an active DowntimeReason
- record optional downtime notes
- automatically record the authenticated User as `opened_by`
- automatically record the downtime start timestamp
- display existing DowntimeEvents on the ProductionRun detail page
- close an open DowntimeEvent
- automatically record the authenticated User as `closed_by`
- automatically record the downtime end timestamp

Existing DowntimeEvent model validation and database constraints remain authoritative.

## DowntimeEvent Website Workflow

The opening workflow is:

```text
ACTIVE ProductionRun
        |
        v
Open Downtime Event
        |
        v
DowntimeEvent form
        |
        v
DowntimeReason selection
        |
        v
ProductionRun state validation
        |
        v
Open-event uniqueness validation
        |
        v
DowntimeEvent created
        |
        v
opened_by assigned automatically
        |
        v
started_at assigned automatically
        |
        v
Redirect to ProductionRun detail page
```

The closing workflow is:

```text
Open DowntimeEvent
        |
        v
Close Downtime Event
        |
        v
POST request
        |
        v
Permission validation
        |
        v
Open-event validation
        |
        v
ended_at assigned automatically
        |
        v
closed_by assigned automatically
        |
        v
DowntimeEvent closed
        |
        v
Redirect to ProductionRun detail page
```

## DowntimeEvent Creation URL

DowntimeEvent creation is scoped to a specific ProductionRun.

The creation endpoint is:

```text
/production-runs/<production_run_pk>/downtime/new/
```

The ProductionRun is determined from the URL.

The User does not manually select a ProductionRun through the form.

This prevents the DowntimeEvent from being reassigned to another ProductionRun through website form input.

## DowntimeEvent Closure URL

An existing open DowntimeEvent is closed through:

```text
/downtime-events/<pk>/close/
```

The DowntimeEvent is identified by its record ID.

Closing downtime changes operational state and therefore requires:

```text
POST
```

Direct GET requests to the close endpoint are rejected.

## DowntimeEvent Form

FO-019 introduces a dedicated ModelForm for DowntimeEvent creation.

The website form exposes:

```text
downtime_reason
notes
```

The following fields are assigned by the application and are not directly editable through the creation form:

```text
production_run
started_at
ended_at
opened_by
closed_by
```

The ProductionRun is assigned from the URL.

The authenticated User is assigned automatically to:

```text
opened_by
```

The downtime start timestamp is assigned automatically using the current application time.

The new DowntimeEvent begins in the open state:

```text
ended_at = None
closed_by = None
```

## DowntimeReason Selection

The DowntimeEvent form uses existing DowntimeReason reference data.

Only active DowntimeReason records are available for selection through the website form.

Inactive DowntimeReason records are excluded from the selectable queryset.

The existing DowntimeReason model and database rules remain unchanged.

## DowntimeEvent Creation Permissions

FO-019 permits DowntimeEvent creation for:

```text
Operator
Production Supervisor
System Administrator
Django superuser
```

Manual and automated verification confirm that Operators and Production Supervisors can use the DowntimeEvent website workflow.

Users outside the permitted manufacturing roles, including Quality Specialist users, cannot open DowntimeEvents through this workflow.

Unauthorised direct access returns:

```text
403 Forbidden
```

The existing Django Group architecture remains the source of role permissions.

FO-019 does not introduce a second role or permission system.

## DowntimeEvent Closure Permissions

Open DowntimeEvents may be closed by:

```text
Operator
Production Supervisor
System Administrator
Django superuser
```

The authenticated User performing the closure is assigned automatically to:

```text
closed_by
```

Users without DowntimeEvent closure permission receive:

```text
403 Forbidden
```

## ProductionRun State Protection

A new DowntimeEvent may only be opened when the related ProductionRun has status:

```text
ACTIVE
```

The following ProductionRun states cannot accept new DowntimeEvents:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

Direct access to the DowntimeEvent creation endpoint for an ineligible ProductionRun returns:

```text
403 Forbidden
```

This server-side protection remains effective even if a User manually enters the endpoint URL.

The existing DowntimeEvent model rule requiring an ACTIVE ProductionRun remains authoritative.

FO-019 does not replace that model validation.

## One Open DowntimeEvent Per ProductionRun

The existing DowntimeEvent database architecture allows a maximum of one open DowntimeEvent for each ProductionRun.

An open DowntimeEvent has:

```text
ended_at = None
```

The database constraint remains:

```text
unique_open_downtime_per_production_run
```

FO-019 also protects this rule at the website workflow level.

When an ACTIVE ProductionRun already has an open DowntimeEvent:

```text
Open Downtime Event
```

is not shown on the ProductionRun detail page.

A second open DowntimeEvent cannot be created for the same ProductionRun.

Once the existing event is closed, another DowntimeEvent may be opened later.

Therefore one ProductionRun may accumulate multiple historical closed DowntimeEvents while still having a maximum of one open event at a time.

## Automatic Opening Traceability

When a valid DowntimeEvent is created through the website:

```text
production_run -> requested ProductionRun
opened_by      -> authenticated User
started_at     -> current application timestamp
ended_at       -> None
closed_by      -> None
```

The User does not manually provide the opening User or opening timestamp.

This preserves consistent operational traceability.

## Closing Downtime

Closing an open DowntimeEvent changes:

```text
ended_at  -> current application timestamp
closed_by -> authenticated User
```

The original values remain unchanged:

```text
production_run
downtime_reason
started_at
opened_by
notes
```

The existing DowntimeEvent consistency rule remains authoritative:

```text
Open:
ended_at = null
closed_by = null

Closed:
ended_at = populated
closed_by = populated
```

## Timestamp Validation

FO-019 preserves the existing timestamp ordering rule:

```text
ended_at >= started_at
```

The database constraint remains:

```text
downtime_event_end_not_before_start
```

The website workflow uses the current application timestamp when closing an event.

FO-019 does not modify or remove the existing model and database validation.

## ProductionRun Detail Integration

FO-019 extends the existing ProductionRun detail page with a:

```text
Downtime Events
```

section.

When no DowntimeEvents exist, the page displays:

```text
No downtime events recorded.
```

When downtime records exist, the section displays operational information including:

```text
Downtime Reason
Downtime Reason description
State
Started At
Ended At
Opened By
Closed By
Notes
```

Open and closed state is derived from the existing DowntimeEvent timestamps.

An open event displays:

```text
Open
```

A closed event displays:

```text
Closed
```

Existing DowntimeEvents remain visible after closure.

FO-019 preserves historical downtime records.

## Open Downtime Event Action

For an authorised User, the ProductionRun detail page displays:

```text
Open Downtime Event
```

only when:

```text
ProductionRun.status = ACTIVE
```

and:

```text
no open DowntimeEvent currently exists for the ProductionRun
```

The action is not displayed when the ProductionRun is:

```text
PLANNED
PAUSED
COMPLETED
CANCELLED
```

The action is also hidden while the ACTIVE ProductionRun already contains an open DowntimeEvent.

After the open event is closed, the action becomes available again while the ProductionRun remains ACTIVE.

## Close Downtime Event Action

An open DowntimeEvent displayed on the ProductionRun detail page provides:

```text
Close Downtime Event
```

to an authorised User.

The action uses POST.

After successful closure:

- the DowntimeEvent displays as Closed
- `ended_at` displays the generated closure timestamp
- `closed_by` displays the authenticated closing User
- the Close Downtime Event action disappears
- the historical DowntimeEvent remains visible
- Open Downtime Event becomes available again if the ProductionRun remains ACTIVE

A closed DowntimeEvent cannot be closed again.

## Downtime Duration

FO-019 does not introduce a new stored downtime-duration field.

The existing DowntimeEvent duration design remains:

```text
duration =
ended_at - started_at
```

for closed events.

Open events have no completed duration.

FO-019 preserves the existing derived-duration architecture.

## ProductionRun Lifecycle Independence

FO-019 does not automatically change ProductionRun lifecycle status.

Opening a DowntimeEvent does not automatically change:

```text
ACTIVE -> PAUSED
```

Closing a DowntimeEvent does not automatically change:

```text
PAUSED -> ACTIVE
```

The existing explicit ProductionRun lifecycle workflows remain independent:

```text
FO-013 Start
FO-014 Pause
FO-015 Resume
FO-016 Complete
FO-017 Cancel
```

Any future automatic ProductionRun lifecycle behaviour based on DowntimeEvent state must be introduced through a separate roadmap issue.

## ProductionEntry Behaviour

FO-019 does not modify ProductionEntry behaviour.

ProductionEntry recording continues to depend on the ProductionRun having status:

```text
ACTIVE
```

FO-019 does not automatically prevent ProductionEntry creation merely because an open DowntimeEvent exists.

Any future rule connecting an open DowntimeEvent to ProductionEntry availability must be explicitly defined by a later issue.

## ProductionRun Completion Behaviour

FO-019 does not introduce a rule requiring open DowntimeEvents to be closed before ProductionRun completion.

The existing FO-016 completion workflow remains unchanged.

Any future completion blocking based on open downtime remains a separate business rule that must be implemented explicitly.

## ProductionRun Cancellation Behaviour

FO-019 does not automatically close open DowntimeEvents when a ProductionRun is cancelled.

The existing FO-017 cancellation workflow remains unchanged.

Any future cancellation propagation into DowntimeEvent state must be explicitly defined and tested through another roadmap issue.

## WorkOrder Behaviour

FO-019 does not automatically modify WorkOrder status.

Opening or closing DowntimeEvent records does not automatically change the associated WorkOrder.

## AuditEvent Behaviour

FO-019 does not automatically create AuditEvent records when downtime is opened or closed.

The existing FO-010 AuditEvent architecture remains unchanged.

Automatic downtime audit logging remains reserved for a future issue that explicitly defines and tests that behaviour.

## QualityInspection Behaviour

FO-019 does not modify QualityInspection behaviour.

QualityInspection remains independent from the DowntimeEvent website workflow.

## Manual FO-019 Verification

FO-019 was manually verified through the ForgeOps website using synthetic manufacturing data.

The primary manual verification used:

```text
Production Run #6
Work Order: WO-2026-0003
Product: PRD-1001 - Synthetic Medical Device Assembly
Production Line: LINE-A01 - Line A
Shift: Night Shift
```

The ProductionRun had existing synthetic ProductionEntry history:

```text
Good Quantity: 136
Rejected Quantity: 14
Total Recorded: 150
Completion: 30.0%
```

The ProductionRun was returned to:

```text
ACTIVE
```

through the existing lifecycle workflow.

The detail page displayed:

```text
Open Downtime Event
```

## DowntimeEvent Opening Verification

A new synthetic DowntimeEvent was opened using:

```text
Downtime Reason: EQUIPMENT - Equipment fault
Notes: Synthetic FO-019 downtime workflow test.
```

After creation, the ProductionRun detail page displayed the new DowntimeEvent with:

```text
State: Open
Downtime Reason: EQUIPMENT
Description: Equipment fault
Started At: populated
Ended At: Not ended
Opened By: admin
Closed By: Not closed
Notes: Synthetic FO-019 downtime workflow test.
```

The page also displayed:

```text
Close Downtime Event
```

The Open Downtime Event action was unavailable while the open event existed.

This confirmed:

- DowntimeEvent creation succeeds against an ACTIVE ProductionRun
- the requested ProductionRun is assigned automatically
- the selected DowntimeReason is stored
- `opened_by` is assigned automatically
- `started_at` is assigned automatically
- new downtime begins open
- `ended_at` remains empty
- `closed_by` remains empty
- existing ProductionEntry history remains unchanged
- the event appears on the ProductionRun detail page

## DowntimeEvent Closure Verification

The synthetic DowntimeEvent was then closed through:

```text
Close Downtime Event
```

After closure, the ProductionRun detail page displayed:

```text
State: Closed
Started At: 15 Aug 2026, 8:56 p.m.
Ended At: 15 Aug 2026, 9:01 p.m.
Opened By: admin
Closed By: admin
```

The existing notes remained:

```text
Synthetic FO-019 downtime workflow test.
```

The Close Downtime Event action disappeared.

The Open Downtime Event action became available again because:

```text
ProductionRun.status = ACTIVE
```

and the ProductionRun no longer contained an open DowntimeEvent.

This confirmed:

- an open DowntimeEvent may be closed successfully
- `ended_at` is generated automatically
- `closed_by` is assigned automatically
- opening traceability is preserved
- closing traceability is recorded
- closed downtime remains visible as operational history
- another downtime event may be opened later

## Ineligible ProductionRun Verification

Direct access to a downtime creation endpoint for a non-ACTIVE ProductionRun was manually tested.

The request returned:

```text
403 Forbidden
```

Server output confirmed:

```text
Downtime Events may only be opened against ACTIVE Production Runs.
```

This verified that DowntimeEvent creation cannot be bypassed by manually entering the URL.

All records used for FO-019 manual verification were synthetic.

## Automated FO-019 Validation

FO-019 introduces a dedicated:

```text
DowntimeEventInterfaceTests
```

test class in:

```text
core/tests.py
```

The dedicated FO-019 test run produced:

```text
Ran 26 tests in 0.794s
OK
```

The automated FO-019 tests verify:

- DowntimeEvent creation requires authentication
- Operator can access the DowntimeEvent creation page for an ACTIVE ProductionRun
- Production Supervisor can access the DowntimeEvent creation page
- unauthorised Quality Specialist cannot access the DowntimeEvent creation page
- Operator can create a valid DowntimeEvent
- Production Supervisor can create a valid DowntimeEvent
- a created DowntimeEvent belongs to the requested ProductionRun
- `opened_by` is assigned automatically
- `started_at` is assigned automatically
- a new DowntimeEvent begins open
- PLANNED ProductionRuns cannot accept DowntimeEvents
- PAUSED ProductionRuns cannot accept DowntimeEvents
- COMPLETED ProductionRuns cannot accept DowntimeEvents
- CANCELLED ProductionRuns cannot accept DowntimeEvents
- Open Downtime Event action is displayed for an eligible ACTIVE ProductionRun
- Open Downtime Event action is hidden for PLANNED ProductionRuns
- Open Downtime Event action is hidden for PAUSED ProductionRuns
- Open Downtime Event action is hidden for COMPLETED ProductionRuns
- Open Downtime Event action is hidden for CANCELLED ProductionRuns
- Open Downtime Event action is hidden when the ACTIVE ProductionRun already has an open DowntimeEvent
- a second simultaneous open DowntimeEvent is blocked
- ProductionRun detail displays an empty downtime state
- ProductionRun detail displays an open DowntimeEvent
- Operator can close an open DowntimeEvent
- Production Supervisor can close an open DowntimeEvent
- unauthorised Quality Specialist cannot close a DowntimeEvent
- closure assigns the closing User
- closure records the end timestamp
- closed downtime no longer exposes the close action
- a closed DowntimeEvent remains visible as historical operational data

Several related assertions are combined within individual tests.

## Full Core Validation

The complete Core regression suite after FO-019 produced:

```text
Ran 262 tests in 21.908s
OK
```

FO-019 therefore adds:

```text
26 tests
```

to the previous FO-018 baseline of:

```text
236 tests
```

resulting in:

```text
262 Core tests
```

Additional verification produced:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected

git diff --check
PASS
```

## Migration Verification

FO-019 does not modify the database schema.

The migration sequence therefore remains:

```text
0001_create_user_groups
0002_create_manufacturing_hierarchy
0003_create_operational_reference_models
0004_create_work_orders_production_runs
0005_create_production_entries
0006_downtimeevent
0007_qualityinspection
0008_auditevent
```

No FO-019 migration is required.

The DowntimeEvent schema introduced in:

```text
0006_downtimeevent
```

remains authoritative.

The existing database constraints remain:

```text
downtime_event_end_not_before_start
downtime_event_close_state_consistent
unique_open_downtime_per_production_run
```

## FO-019 Files Updated

FO-019 updates:

```text
core/forms.py
core/views.py
core/urls.py
core/tests.py
core/templates/core/production_run_detail.html
core/templates/core/downtime_event_form.html
docs/database-design.md
```

## FO-019 Acceptance Criteria Verified

- DowntimeEvent website workflow is implemented.
- DowntimeEvent creation requires authentication.
- DowntimeEvent creation is associated with a specific ProductionRun.
- ProductionRun is determined by the endpoint rather than editable form input.
- DowntimeEvent form exposes DowntimeReason.
- DowntimeEvent form exposes optional notes.
- ProductionRun is not directly editable through the form.
- `opened_by` is assigned automatically from the authenticated User.
- `started_at` is assigned automatically.
- new DowntimeEvents begin open.
- new DowntimeEvents contain no `ended_at`.
- new DowntimeEvents contain no `closed_by`.
- only active DowntimeReasons are selectable.
- Operators can open DowntimeEvents.
- Production Supervisors can open DowntimeEvents.
- System Administrator permission is implemented in permission logic.
- Django superuser permission is implemented.
- unauthorised roles cannot open DowntimeEvents.
- DowntimeEvent creation is allowed against ACTIVE ProductionRuns.
- PLANNED ProductionRuns cannot accept DowntimeEvents.
- PAUSED ProductionRuns cannot accept DowntimeEvents.
- COMPLETED ProductionRuns cannot accept DowntimeEvents.
- CANCELLED ProductionRuns cannot accept DowntimeEvents.
- direct creation access for an ineligible ProductionRun returns 403 Forbidden.
- only one open DowntimeEvent may exist for a ProductionRun.
- a second simultaneous open DowntimeEvent is blocked.
- Open Downtime Event is displayed only for eligible ACTIVE ProductionRuns.
- Open Downtime Event is hidden when an open DowntimeEvent already exists.
- Open Downtime Event is hidden for PLANNED ProductionRuns.
- Open Downtime Event is hidden for PAUSED ProductionRuns.
- Open Downtime Event is hidden for COMPLETED ProductionRuns.
- Open Downtime Event is hidden for CANCELLED ProductionRuns.
- ProductionRun detail includes a Downtime Events section.
- an empty downtime state is displayed when no events exist.
- open DowntimeEvents are displayed on the ProductionRun detail page.
- closed DowntimeEvents remain displayed as historical records.
- open and closed states are visually distinguishable.
- open DowntimeEvents may be closed through the website.
- downtime closure requires POST.
- Operator can close an eligible open DowntimeEvent.
- Production Supervisor can close an eligible open DowntimeEvent.
- unauthorised roles cannot close DowntimeEvents.
- `closed_by` is assigned automatically from the authenticated User.
- `ended_at` is assigned automatically.
- the original opening User remains unchanged.
- the original opening timestamp remains unchanged.
- DowntimeReason remains unchanged during closure.
- notes remain unchanged during closure.
- closed DowntimeEvents cannot be closed again.
- existing timestamp ordering validation remains authoritative.
- existing close-state consistency validation remains authoritative.
- existing one-open-event-per-run database constraint remains authoritative.
- downtime duration remains derived from timestamps.
- no duplicate duration field is introduced.
- existing ProductionRun Start workflow remains functional.
- existing ProductionRun Pause workflow remains functional.
- existing ProductionRun Resume workflow remains functional.
- existing ProductionRun Completion workflow remains functional.
- existing ProductionRun Cancellation workflow remains functional.
- existing ProductionEntry website workflow remains functional.
- opening downtime does not automatically pause the ProductionRun.
- closing downtime does not automatically resume the ProductionRun.
- an open DowntimeEvent does not automatically block ProductionRun completion.
- ProductionRun cancellation does not automatically close downtime.
- no automatic WorkOrder status change is introduced.
- no automatic AuditEvent creation is introduced.
- no QualityInspection behaviour is changed.
- no database migration is introduced.
- all manual test data is synthetic.
- 26 dedicated FO-019 tests pass.
- 262 Core tests pass.
- Django system checks pass.
- migration drift check passes.
- Git whitespace validation passes.

## FO-019 Out of Scope

FO-019 does not implement:

- DowntimeEvent editing after creation
- DowntimeEvent deletion
- DowntimeEvent correction workflow
- DowntimeEvent approval workflow
- DowntimeEvent electronic signatures
- reopening a closed DowntimeEvent
- modifying `started_at` through the website
- modifying `ended_at` manually through the website
- manually selecting `opened_by`
- manually selecting `closed_by`
- automatic ProductionRun pause when downtime opens
- automatic ProductionRun resume when downtime closes
- automatic ProductionRun status transitions from DowntimeEvent state
- automatic ProductionEntry blocking while an open DowntimeEvent exists
- blocking ProductionRun completion while downtime remains open
- automatic DowntimeEvent closure during ProductionRun completion
- automatic DowntimeEvent closure during ProductionRun cancellation
- automatic WorkOrder status changes
- automatic AuditEvent creation for downtime opening
- automatic AuditEvent creation for downtime closure
- downtime approval workflow
- downtime reason management through the normal website
- downtime reason creation through the normal website
- downtime dashboards
- downtime analytics
- downtime Pareto analysis
- OEE calculation
- MTBF calculation
- MTTR calculation
- machine integration
- PLC integration
- MES integration
- REST API endpoints
- external downtime import
- real manufacturing data
- QualityInspection website workflow

These behaviours remain reserved for future roadmap issues that explicitly define them.

All test and demonstration data must remain synthetic.