# ForgeOps MVP Wireframes

## Purpose

These low-fidelity wireframes define the initial page layout and information hierarchy for the ForgeOps MVP.

They focus on workflow and usability rather than colours, branding or visual polish.

---

# 1. Login Page

```text
┌──────────────────────────────────────────────────────────────┐
│                         FORGEOPS                             │
│          Manufacturing Operations Intelligence              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    Sign in to ForgeOps                       │
│                                                              │
│     Username                                                 │
│     ┌──────────────────────────────────────────────────┐     │
│     │                                                  │     │
│     └──────────────────────────────────────────────────┘     │
│                                                              │
│     Password                                                 │
│     ┌──────────────────────────────────────────────────┐     │
│     │                                                  │     │
│     └──────────────────────────────────────────────────┘     │
│                                                              │
│                  [ Sign In ]                                 │
│                                                              │
│     Error messages appear here when login fails.             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Username field
- Password field
- Sign-in button
- Clear authentication errors
- Educational project disclaimer
- No self-registration in the MVP

---

# 2. Operator Dashboard

```text
┌─────────────────────────────────────────────────────────────────────┐
│ ForgeOps          Operator Dashboard           User: Alex | Logout │
├─────────────────────────────────────────────────────────────────────┤
│ Assigned Production Runs                                            │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Run       Work Order   Product     Line   Shift       Status    │ │
│ │ PR-001    WO-1001      Product A   L01    Day Shift   Active    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Current Run                                                         │
│                                                                     │
│ Work Order: WO-1001        Product: Product A                       │
│ Planned Quantity: 1,000    Status: Active                           │
│                                                                     │
│ Good: 620    Rejected: 18    Remaining: 380                         │
│                                                                     │
│ [ Record Output ]   [ Open Downtime ]   [ View Inspection Status ] │
│                                                                     │
│ Recent Entries                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Time       Good     Rejected     Recorded By                    │ │
│ │ 10:30      120      3            Alex                           │ │
│ │ 11:15      150      5            Alex                           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Show only assigned production runs
- Clearly display current run status
- Show planned and recorded quantities
- Provide direct access to output and downtime actions
- Prevent entry when the run is not active

---

# 3. Record Production Output

```text
┌──────────────────────────────────────────────────────────────┐
│ Record Production Output                                     │
├──────────────────────────────────────────────────────────────┤
│ Work Order: WO-1001                                          │
│ Product: Product A                                           │
│ Production Line: L01                                         │
│ Run Status: Active                                           │
│                                                              │
│ Good Quantity                                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │                                                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Rejected Quantity                                            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │                                                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Notes                                                        │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │                                                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ [ Cancel ]                              [ Save Entry ]       │
│                                                              │
│ Validation messages appear beside invalid fields.            │
└──────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Good and rejected quantities
- Whole-number validation
- No negative quantities
- At least one quantity greater than zero
- Optional notes
- Clear confirmation after saving

---

# 4. Supervisor Work-Order Page

```text
┌─────────────────────────────────────────────────────────────────────┐
│ ForgeOps        Production Supervisor          User: Sara | Logout │
├─────────────────────────────────────────────────────────────────────┤
│ [ Dashboard ] [ Work Orders ] [ Production Runs ] [ Downtime ]     │
│                                                                     │
│ Work Orders                                      [ Create Work Order ]│
│                                                                     │
│ Filters: [ Status ▼ ] [ Product ▼ ] [ Date Range ] [ Search ]      │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Number   Product    Planned   Date       Status       Action    │ │
│ │ WO-1001  Product A  1,000     01 Aug     In Progress  View      │ │
│ │ WO-1002  Product B  2,000     02 Aug     Planned      Assign    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Selected Work Order                                                 │
│                                                                     │
│ Product: Product B             Planned Quantity: 2,000               │
│ Production Date: 02 Aug        Status: Planned                      │
│                                                                     │
│ Production Line: [ Select ▼ ]                                       │
│ Shift:          [ Select ▼ ]                                        │
│ Operator:       [ Select ▼ ]                                        │
│                                                                     │
│ [ Cancel Work Order ]                [ Create Production Run ]       │
└─────────────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Create and view work orders
- Filter work orders
- Assign line, shift and operator
- Display current status
- Prevent invalid assignments
- Confirm cancellation actions

---

# 5. Quality Inspection Page

```text
┌──────────────────────────────────────────────────────────────┐
│ ForgeOps                    Quality Inspection               │
├──────────────────────────────────────────────────────────────┤
│ Work Order: WO-1001                                          │
│ Production Run: PR-001                                       │
│ Product: Product A                                           │
│ Line: L01                                                    │
│                                                              │
│ Production Summary                                           │
│ Good Quantity: 1,000                                         │
│ Rejected Quantity: 24                                        │
│ Total Downtime: 35 minutes                                   │
│                                                              │
│ Inspection Result                                            │
│                                                              │
│ ( ) Passed                                                   │
│ ( ) Failed                                                   │
│                                                              │
│ Inspection Notes                                             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │                                                          │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ [ Cancel ]                         [ Save Inspection ]       │
│                                                              │
│ Failed results are highlighted to authorised users.          │
└──────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Display production context
- Allow Passed or Failed result
- Require a result before saving
- Require notes for failed inspections
- Record inspector and completion time
- Prevent unauthorised editing

---

# 6. Operations Manager Dashboard

```text
┌─────────────────────────────────────────────────────────────────────┐
│ ForgeOps           Operations Dashboard         User: Maya | Logout│
├─────────────────────────────────────────────────────────────────────┤
│ Filters                                                            │
│ [ Date Range ] [ Production Line ▼ ] [ Product ▼ ] [ Shift ▼ ]     │
│                                                                     │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────────┐     │
│ │ Planned    │ │ Good       │ │ Rejected   │ │ Downtime      │     │
│ │ 10,000     │ │ 9,420      │ │ 280        │ │ 310 minutes   │     │
│ └────────────┘ └────────────┘ └────────────┘ └───────────────┘     │
│                                                                     │
│ ┌────────────┐ ┌────────────┐ ┌──────────────────────────────┐     │
│ │ Completion │ │ Rejection  │ │ Failed Inspections           │     │
│ │ 94.2%      │ │ 2.9%       │ │ 3                            │     │
│ └────────────┘ └────────────┘ └──────────────────────────────┘     │
│                                                                     │
│ Planned Versus Good Output                                          │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                         Chart                                   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Downtime by Reason                                                  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                         Chart                                   │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Runs Requiring Attention                                            │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Run      Line      Issue                     Status              │ │
│ │ PR-008   L02       Failed inspection         Review required     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Display key operational metrics
- Support date, line, product and shift filters
- Highlight failed inspections
- Highlight underperforming runs
- Use stored system data for every calculation
- Provide read-only access for managers

---

# 7. Audit-History Page

```text
┌─────────────────────────────────────────────────────────────────────┐
│ ForgeOps                   Audit History                            │
├─────────────────────────────────────────────────────────────────────┤
│ Filters                                                             │
│ [ User ▼ ] [ Action Type ▼ ] [ Record Type ▼ ] [ Date Range ]      │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ Time       User      Action     Record       Description         │ │
│ │ 09:15      Sara      Created    WO-1001      Work order created  │ │
│ │ 09:22      Alex      Started    PR-001       Run started         │ │
│ │ 10:10      Alex      Opened     DT-004       Downtime opened     │ │
│ │ 10:35      Alex      Closed     DT-004       Downtime closed     │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ Audit records are read-only.                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Main Requirements

- Show user, action, time and affected record
- Filter by user, action, record type and date
- Keep records read-only
- Restrict access to authorised roles
- Do not provide edit or delete buttons

---

# Shared Navigation Rules

Navigation options must depend on the user's role.

## Operator

- Assigned Runs
- Record Output
- Downtime
- Logout

## Production Supervisor

- Dashboard
- Work Orders
- Production Runs
- Downtime
- Logout

## Quality Specialist

- Inspections
- Production Records
- Logout

## Manufacturing Engineer

- Production Analytics
- Downtime Analysis
- Quality Trends
- Logout

## Operations Manager

- Operations Dashboard
- Production Results
- Quality Summary
- Logout

## System Administrator

- Users
- Products
- Production Lines
- Shifts
- Downtime Reasons
- Audit History
- Logout

---

# Wireframe Decisions

1. The interface will use role-specific navigation.
2. Operators will see their current assigned run immediately after login.
3. Important actions will be available without navigating through several pages.
4. Managers will receive primarily read-only dashboards.
5. Failed inspections and open downtime will be visually prominent.
6. Destructive actions will require confirmation.
7. Validation errors will appear beside the relevant fields.
8. Visual styling will be added after the workflows are functional.