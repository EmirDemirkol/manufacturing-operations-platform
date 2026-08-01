# ForgeOps MVP Production Workflow

## Purpose

This workflow describes the main ForgeOps production process from work-order creation to management reporting.

It is a BPMN-style workflow represented using Mermaid. Each section represents a user role or the ForgeOps system.

```mermaid
flowchart TD

    START([Production requirement identified])

    subgraph SUPERVISOR[Production Supervisor]
        S1[Create work order]
        S2[Select product and planned quantity]
        S3[Assign production line, shift and operator]
        S4[Release production run]
        S5[Review final production results]
        S6{Completion requirements satisfied?}
        S7[Complete production run]
        S8[Return run for correction]
    end

    subgraph SYSTEM[ForgeOps System]
        SYS1[Validate work-order information]
        SYS2[Create work order and audit event]
        SYS3[Create production run with Not Started status]
        SYS4[Record actual start time]
        SYS5[Change run status to Active]
        SYS6[Update production totals]
        SYS7[Open downtime event]
        SYS8[Change run status to Paused]
        SYS9[Calculate downtime duration]
        SYS10[Change run status back to Active]
        SYS11[Store inspection result]
        SYS12[Check open downtime and inspection status]
        SYS13[Lock completed operational records]
        SYS14[Update production dashboard]
        SYS15[Create audit events]
    end

    subgraph OPERATOR[Operator]
        O1[View assigned production run]
        O2[Start production run]
        O3[Record good and rejected quantities]
        O4{Did production stop?}
        O5[Select downtime reason and open downtime]
        O6[Resolve production issue]
        O7[Close downtime event]
        O8[Continue recording production]
        O9[Submit run for supervisor review]
    end

    subgraph QUALITY[Quality Specialist]
        Q1[Open production-run inspection]
        Q2[Perform final quality inspection]
        Q3{Inspection passed?}
        Q4[Record Passed result]
        Q5[Record Failed result and notes]
    end

    subgraph MANAGER[Operations Manager]
        M1[View production dashboard]
        M2[Review planned versus actual output]
        M3[Review rejection rate and downtime]
        M4[Identify performance issues]
    end

    START --> S1
    S1 --> S2
    S2 --> SYS1

    SYS1 -->|Valid| SYS2
    SYS1 -->|Invalid| S1

    SYS2 --> S3
    S3 --> SYS3
    SYS3 --> S4
    S4 --> O1

    O1 --> O2
    O2 --> SYS4
    SYS4 --> SYS5
    SYS5 --> SYS15
    SYS15 --> O3

    O3 --> SYS6
    SYS6 --> O4

    O4 -->|No| O8
    O4 -->|Yes| O5

    O5 --> SYS7
    SYS7 --> SYS8
    SYS8 --> O6
    O6 --> O7
    O7 --> SYS9
    SYS9 --> SYS10
    SYS10 --> O8

    O8 --> O3
    O8 -->|Production finished| Q1

    Q1 --> Q2
    Q2 --> Q3

    Q3 -->|Yes| Q4
    Q4 --> SYS11
    SYS11 --> O9

    Q3 -->|No| Q5
    Q5 --> SYS11
    SYS11 --> S8
    S8 --> O3

    O9 --> S5
    S5 --> SYS12
    SYS12 --> S6

    S6 -->|No| S8
    S6 -->|Yes| S7

    S7 --> SYS13
    SYS13 --> SYS14
    SYS14 --> SYS15
    SYS15 --> M1

    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> END([Workflow complete])
```

## Main Workflow Summary

1. The supervisor creates a work order.
2. ForgeOps validates and stores the work order.
3. The supervisor assigns the production line, shift and operator.
4. The operator starts the production run.
5. ForgeOps records the start time and changes the run status to Active.
6. The operator records good and rejected quantities.
7. If production stops, the operator opens a downtime event.
8. ForgeOps pauses the production run and records the downtime.
9. The operator closes the downtime event when the issue is resolved.
10. A quality specialist performs the final inspection.
11. A failed inspection returns the run for correction.
12. A passed inspection allows the supervisor to review completion requirements.
13. The supervisor completes the production run.
14. ForgeOps locks the completed records and updates the dashboard.
15. The operations manager reviews production performance.

## Completion Requirements

A production run can only be completed when:

- The production run is active or awaiting review.
- No downtime event remains open.
- At least one final inspection has passed.
- Production quantities have been recorded.
- The supervisor has permission to complete the run.

## Audit Events

ForgeOps records audit events when:

- A work order is created.
- A production run is assigned.
- A production run is started.
- Production output is recorded.
- Downtime is opened or closed.
- An inspection result is recorded.
- A production run is completed.