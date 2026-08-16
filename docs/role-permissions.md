# ForgeOps Role-Permission Matrix

## Purpose

This document defines the permissions assigned to each ForgeOps user role.

Permissions must be enforced on the server. Hiding a button in the interface is not sufficient protection.

The matrix reflects the currently implemented ForgeOps website behaviour where that behaviour has been explicitly defined and tested.

Future roadmap behaviour must not be treated as implemented until a dedicated issue defines and verifies it.

All test and demonstration data must remain synthetic.

## Roles

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer
- Operations Manager
- System Administrator

## Permission Levels

- **Create**: Add a new record.
- **View**: Read an existing record.
- **Update**: Change an existing record.
- **Complete**: Move a record into its completed state.
- **Configure**: Manage system reference data.
- **No Access**: The user cannot view or perform the action.

---

## Permission Matrix

| Action | Operator | Supervisor | Quality Specialist | Manufacturing Engineer | Operations Manager | System Administrator |
|---|---|---|---|---|---|---|
| Log in and log out | Yes | Yes | Yes | Yes | Yes | Yes |
| View own profile | Yes | Yes | Yes | Yes | Yes | Yes |
| Manage users and roles | No | No | No | No | No | Yes |
| Configure products | No | No | No | No | No | Yes |
| Configure production lines | No | No | No | No | No | Yes |
| Configure shifts | No | No | No | No | No | Yes |
| Configure downtime reasons | No | No | No | No | No | Yes |
| View work orders | Assigned only | Yes | Yes | Yes | Yes | Configuration support only |
| Create work orders | No | Yes | No | No | No | No |
| Update planned work orders | No | Yes | No | No | No | No |
| Cancel work orders | No | Yes | No | No | No | No |
| Create production runs | No | Yes | No | No | No | No |
| Assign operators | No | Yes | No | No | No | No |
| View production runs | Assigned only | Yes | Yes | Yes | Yes | Configuration support only |
| Start production runs | Assigned only | Yes | No | No | No | No |
| Record good quantities | Active assigned runs | Yes | No | No | No | No |
| Record rejected quantities | Active assigned runs | Yes | No | No | No | No |
| Update own production entry | Before run completion | Yes | No | No | No | No |
| Delete production entries | No | Restricted correction only | No | No | No | No |
| Open downtime event | Active assigned runs | Yes | No | No | No | No |
| Close downtime event | Own assigned run | Yes | No | No | No | No |
| View downtime records | Assigned runs | Yes | Yes | Yes | Yes | Audit support only |
| Create quality inspection | No | No | Yes | No | No | No |
| Record inspection result | No | No | Yes | No | No | No |
| Update inspection result | No | No | Before run completion | No | No | No |
| View inspection results | Relevant runs | Yes | Yes | Yes | Yes | Audit support only |
| Complete production run | No | Yes | No | No | No | No |
| View line dashboard | Limited assigned data | Yes | Yes | Yes | Yes | No |
| View site-level dashboard | No | Limited | Limited | Yes | Yes | No |
| View audit history | No | No | No | No | Yes | Yes |
| Edit audit records | No | No | No | No | No | No |

---

## Core Permission Rules

### Rule 1: Least Privilege

Every role receives only the permissions required to perform its responsibilities.

Permissions must be introduced deliberately through defined ForgeOps workflows.

A role should not gain additional operational access merely because it has broad platform visibility.

### Rule 2: Assigned Production Access

Operators can only access Production Runs assigned to them unless an authorised workflow explicitly grants additional access.

Assigned-production behaviour remains subject to the implementation state of the relevant roadmap issue.

### Rule 3: Completed Record Protection

After a Production Run is completed:

- Operators cannot add new Production Entries.
- Operators cannot change quantities through normal workflows.
- Downtime Events cannot be opened.
- completed Quality Inspection records cannot be completed again.
- completed Production Runs cannot be restarted, paused, resumed, completed again or cancelled through the implemented lifecycle workflows.
- corrections require an authorised process.
- any associated automatic AuditEvent creation must be introduced through a future workflow that explicitly defines and tests it.

### Rule 4: Audit Record Protection

Existing AuditEvent records are immutable through the normal ForgeOps website interface.

The FO-022 Audit Event interface is read only and does not provide create, edit or delete controls.

Existing AuditEvent records are also read only through normal Django administration.

AuditEvent deletion is disabled through normal Django administration.

Synthetic AuditEvent records may be entered manually through Django administration for development and verification purposes.

ForgeOps does not currently create AuditEvent records automatically for every operational action.

Automatic AuditEvent generation remains reserved for future roadmap issues that explicitly define and test the relevant behaviour.

### Rule 5: Manager Access

Operations Managers mainly receive read-only operational access.

They can inspect dashboards, production information and AuditEvent history where an implemented workflow permits it.

FO-022 explicitly permits Operations Managers to access the read-only Audit Event website interface.

Operations Managers do not normally create or modify production records through current ForgeOps operational workflows.

### Rule 6: Administrator Separation

The System Administrator role is primarily responsible for platform and configuration administration.

The role is associated with responsibilities such as:

- Users
- Roles
- Products
- Production Lines
- Shifts
- Downtime Reasons
- System configuration
- Audit access

The System Administrator role does not automatically own manufacturing decisions merely because it manages the platform.

Individual ForgeOps workflows may explicitly grant the System Administrator additional permissions.

Where such permission exists, it must be defined and enforced by that workflow.

FO-022 explicitly permits System Administrators to access the read-only Audit Event interface.

### Rule 7: Server-Side Enforcement

Every permission must be checked by Django on the server.

Interface controls may hide unavailable actions, but hidden buttons are not security controls.

Unauthorised requests must still be rejected by the server when a User manually enters or submits a restricted endpoint.

Implemented ForgeOps workflows currently use controlled responses such as:

```text
403 Forbidden
```

for authenticated Users who attempt unauthorised actions.

Unauthenticated Users are redirected through the authentication workflow where appropriate.

### Rule 8: Audit Event Roadmap

FO-022 provides read-only website access to existing AuditEvent records.

The following operational actions remain candidates for future automatic AuditEvent generation:

- User or role creation
- Configuration changes
- WorkOrder creation or cancellation
- ProductionRun assignment
- ProductionRun lifecycle transitions
- Production quantity entry
- Downtime opening or closing
- Quality Inspection creation or completion
- Authorised record correction

These actions do not automatically create AuditEvent records unless a future roadmap issue explicitly implements and tests that behaviour.

### Rule 9: Audit History Access

The implemented FO-022 Audit Event website interface is available to:

- Operations Manager
- System Administrator
- Django superuser

The following roles do not have access to the FO-022 Audit Event website interface:

- Operator
- Production Supervisor
- Quality Specialist
- Manufacturing Engineer

Authenticated Users without permission receive:

```text
403 Forbidden
```

Django superuser access is implemented as an application-level override and is not represented as a separate column in the role matrix.

### Rule 10: Audit Interface Scope

The FO-022 Audit Event interface is available at:

```text
/audit-events/
```

It displays existing AuditEvent records including:

- created timestamp
- responsible User
- action type
- record type
- record identifier
- description

The interface supports filtering by:

- Action Type
- Record Type

The interface remains read only.

It does not provide:

- AuditEvent creation
- AuditEvent editing
- AuditEvent deletion
- automatic AuditEvent generation
- audit export
- regulatory audit certification
- electronic signatures
- SIEM integration

These behaviours remain reserved for future roadmap issues that explicitly define them.

---

## Current AuditEvent Behaviour

The current AuditEvent architecture was introduced in FO-010.

AuditEvent records contain:

- User
- Action Type
- Record Type
- Record Identifier
- Description
- Created timestamp

Controlled Action Type values are:

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

Existing AuditEvent records are ordered newest first.

The affected operational record is identified using:

```text
record_type
record_identifier
```

rather than a direct foreign key to every possible ForgeOps model.

The AuditEvent User relationship uses protected deletion.

A User referenced by an AuditEvent cannot be deleted while the AuditEvent exists.

---

## FO-022 Audit Access Decisions

FO-022 resolves the website access rules for existing AuditEvent history.

Allowed:

```text
Operations Manager
System Administrator
Django superuser
```

Blocked:

```text
Operator
Production Supervisor
Quality Specialist
Manufacturing Engineer
```

The interface is read only.

The permission is enforced in Django server-side logic.

The interface does not depend on hidden navigation elements for protection.

FO-022 does not implement record-level audit visibility for Supervisors, Quality Specialists or Manufacturing Engineers.

Any future limited or record-specific audit access must be introduced through another roadmap issue that explicitly defines the visibility rules.

---

## Initial Access Decisions

1. Operators only see assigned Production Runs where the relevant workflow supports assignment-aware access.
2. Production Supervisors control defined ProductionRun lifecycle and manufacturing workflows.
3. Quality Specialists control the implemented QualityInspection website workflow.
4. Manufacturing Engineers mainly analyse operational data and do not currently receive FO-022 Audit Event access.
5. Operations Managers receive primarily read-only access and may view FO-022 Audit Event history.
6. System Administrators manage the platform and may view FO-022 Audit Event history.
7. Django superusers retain application-level override access where the implemented workflow explicitly supports it.
8. Completed operational records are protected against unsupported lifecycle changes.
9. Existing AuditEvent records are read only through the normal ForgeOps website interface.
10. Existing AuditEvent records are read only through normal Django administration.
11. AuditEvent deletion is disabled through normal Django administration.
12. Synthetic AuditEvent records may be manually entered through Django administration for development and verification.
13. Automatic AuditEvent generation is not currently implemented globally.
14. Future automatic audit behaviour must be introduced only through roadmap issues that explicitly define and test it.
15. All test and demonstration data must remain synthetic.