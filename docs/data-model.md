# Data model

> Owned by the **Architect** agent. Co-authored with the **Data Engineer** agent.

## Star schema (PostgreSQL + PostGIS)

See `docs/IMPLEMENTATION_PLAN.md` §4.2 for the full DDL. This file summarises the design.

### Fact table

```sql
fact_crime (
  crime_id       BIGSERIAL PRIMARY KEY,
  time_id        INT REFERENCES dim_time(time_id),
  location_id    INT REFERENCES dim_location(location_id),
  offense_id     INT REFERENCES dim_offense(offense_id),
  case_id        INT REFERENCES dim_case(case_id),
  arrest         BOOLEAN NOT NULL,
  domestic       BOOLEAN NOT NULL,
  beat           VARCHAR(4),
  fbi_code       VARCHAR(4)
)
```

### Dimension tables

| Table | PK | Key columns | Notes |
|---|---|---|---|
| `dim_case` | `case_id` | `case_number` (UNIQUE), `updated_on` | One row per unique case_number |
| `dim_time` | `time_id` | `ts`, `date`, `day`, `month`, `year`, `hour`, `weekday`, `is_weekend` | Pre-populated; 1 row per hour |
| `dim_location` | `location_id` | `block`, `location_description`, `latitude`, `longitude`, `district`, `ward`, `community_area`, `geom` (PostGIS Point) | PostGIS GIST index on `geom` |
| `dim_offense` | `offense_id` | `iucr` (UNIQUE), `primary_type`, `description`, `fbi_code` | Mapped from IUCR codes |

### dbt marts

See `docs/IMPLEMENTATION_PLAN.md` §4.3 for the full list. Seven marts, each owned by the Data Engineer agent, consumed by the Backend agent.

### Indexes

```sql
CREATE INDEX idx_fact_crime_time      ON fact_crime (time_id);
CREATE INDEX idx_fact_crime_location  ON fact_crime (location_id);
CREATE INDEX idx_fact_crime_offense   ON fact_crime (offense_id);
CREATE INDEX idx_dim_time_date        ON dim_time (date);
CREATE INDEX idx_dim_location_geom    ON dim_location USING GIST (geom);
```
