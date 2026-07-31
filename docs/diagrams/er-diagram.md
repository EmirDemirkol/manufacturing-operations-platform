# ForgeOps MVP Entity-Relationship Diagram

This diagram represents the initial ForgeOps MVP database structure.

```mermaid
erDiagram

    USER {
        int id PK
        string username
        string email
        boolean is_active
    }

    SITE {
        int id PK
        string site_code UK
        string site_name
        string location
        boolean is_active
    }

    PRODUCT {
        int id PK
        string product_code UK
        string product_name
        string description
        boolean is_active
    }

    PRODUCTION_LINE {
        int id PK
        int site_id FK
        string line_code UK
        string line_name
        boolean is_active
    }

    SHIFT {
        int id PK
        string shift_name UK
        time start_time
        time end_time
        boolean is_active
    }

    WORK_ORDER {
        int id PK
        int product_id FK
        string work_order_number UK
        int planned_quantity
        date planned_production_date
        string status
        int created_by_id FK
    }

    PRODUCTION_RUN {
        int id PK
        int work_order_id FK
        int production_line_id FK
        int shift_id FK
        int assigned_operator_id FK
        string status
        datetime actual_start
        datetime actual_completion
        int created_by_id FK
    }

    PRODUCTION_ENTRY {
        int id PK
        int production_run_id FK
        int good_quantity
        int rejected_quantity
        int recorded_by_id FK
        datetime recorded_at
        string notes
    }

    DOWNTIME_REASON {
        int id PK
        string reason_code UK
        string reason_name
        string description
        boolean is_active
    }

    DOWNTIME_EVENT {
        int id PK
        int production_run_id FK
        int downtime_reason_id FK
        datetime start_time
        datetime end_time
        int opened_by_id FK
        int closed_by_id FK
        string notes
    }

    QUALITY_INSPECTION {
        int id PK
        int production_run_id FK
        string result
        string notes
        int completed_by_id FK
        datetime completed_at
    }

    AUDIT_EVENT {
        int id PK
        int user_id FK
        string action_type
        string record_type
        string record_identifier
        string description
        datetime event_time
    }

    SITE ||--o{ PRODUCTION_LINE : contains

    PRODUCT ||--o{ WORK_ORDER : planned_for

    WORK_ORDER ||--o{ PRODUCTION_RUN : has

    PRODUCTION_LINE ||--o{ PRODUCTION_RUN : hosts

    SHIFT ||--o{ PRODUCTION_RUN : schedules

    USER ||--o{ WORK_ORDER : creates

    USER ||--o{ PRODUCTION_RUN : assigned_to

    USER ||--o{ PRODUCTION_RUN : creates

    PRODUCTION_RUN ||--o{ PRODUCTION_ENTRY : contains

    USER ||--o{ PRODUCTION_ENTRY : records

    PRODUCTION_RUN ||--o{ DOWNTIME_EVENT : experiences

    DOWNTIME_REASON ||--o{ DOWNTIME_EVENT : categorises

    USER ||--o{ DOWNTIME_EVENT : opens

    USER ||--o{ DOWNTIME_EVENT : closes

    PRODUCTION_RUN ||--o{ QUALITY_INSPECTION : requires

    USER ||--o{ QUALITY_INSPECTION : completes

    USER ||--o{ AUDIT_EVENT : generates
```

## Relationship Explanation

- One site contains many production lines.
- One product may have many work orders.
- One work order may have multiple production runs.
- One production line may host many production runs.
- One shift may be used by many production runs.
- One operator may be assigned to many runs over time, but only one may be active at a time.
- One production run may contain many production entries.
- One production run may experience many downtime events.
- One downtime reason may be used by many downtime events.
- One production run may have many quality inspections.
- One user may generate many audit events.

## Key

- `PK` means Primary Key.
- `FK` means Foreign Key.
- `UK` means Unique Key.
- `||` means exactly one.
- `o{` means zero or many.