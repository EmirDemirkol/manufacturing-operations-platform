# ForgeOps Role-Permission Matrix

## Purpose

This document defines the permissions assigned to each ForgeOps user role.

Permissions must be enforced on the server. Hiding a button in the interface is not sufficient protection.

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
| View audit history | No | Limited relevant records | Limited relevant records | Read only | Read only | Yes |
| Edit audit records | No | No | No | No | No | No |

---

## Core Permission Rules

### Rule 1: Least Privilege

Every role receives only the permissions required to perform its responsibilities.

### Rule 2: Assigned Production Access

Operators can only access production runs assigned to them unless an authorised supervisor grants additional access.

### Rule 3: Completed Record Protection

After a production run is completed:

- Operators cannot add new production entries.
- Operators cannot change quantities.
- Downtime events cannot be opened.
- Inspection results cannot be changed through normal workflows.
- Corrections require an authorised process and must create an audit event.

### Rule 4: Audit Record Protection

Audit records are created automatically by the system.

No user, including the system administrator, can edit or delete audit records through the normal application interface.

### Rule 5: Manager Access

Operations managers mainly have read-only access.

They can view dashboards, production results, downtime, inspections and audit information, but they do not normally create or alter operational records.

### Rule 6: Administrator Separation

The system administrator manages:

- Users
- Roles
- Products
- Production lines
- Shifts
- Downtime reasons
- System configuration
- Audit access

The system administrator does not automatically receive permission to create or alter production records.

### Rule 7: Server-Side Enforcement

Every permission must be checked by Django on the server.

Interface controls may hide unavailable actions, but the server must still reject unauthorised requests.

### Rule 8: Audit Events

The following actions must create audit events:

- User or role creation
- Configuration changes
- Work-order creation or cancellation
- Production-run assignment
- Production-run start
- Production quantity entry
- Downtime opening or closing
- Inspection creation or update
- Production-run completion
- Authorised record correction

---

## Initial Access Decisions

1. Operators only see assigned production runs.
2. Supervisors control work orders and production-run completion.
3. Quality specialists control inspection results.
4. Manufacturing engineers analyse data but do not alter production records.
5. Operations managers receive primarily read-only access.
6. System administrators manage the platform but do not own production decisions.
7. Completed records are locked against normal editing.
8. Audit records are immutable through the application.