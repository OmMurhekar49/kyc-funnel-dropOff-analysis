# Paper 2: Technology Research
## Python, Pandas, NumPy, SQL/MySQL, SQLAlchemy and Power BI in a Funnel-Analysis Workflow

> **Scope honesty:** describes how each tool is used *in this project*. General descriptions of the tools are
> standard background, cited from official documentation at the end of this paper.

---

### 1. Overview and workflow
```
Faker + NumPy/random  ->  Pandas DataFrames  ->  MySQL (fact tables)  ->  SQL analysis queries
                                                        |
                              SQLAlchemy + mysql-connector-python
                                                        |
                        Jupyter notebook: Pandas/NumPy + Matplotlib/Seaborn
                                                        |
                                              CSV exports  ->  Power BI dashboard
```
Each tool has a distinct role. The design principle: **do heavy set-based work in SQL, exploratory and statistical
work in Python, and stakeholder-facing communication in Power BI.**

### 2. Python
**What it is:** a general-purpose language with a large data ecosystem.
**Role here:** glue. It generates the data, loads it into MySQL, queries it back, analyses it and exports it.
**Why chosen:** the analyst already knows it, the library ecosystem covers every step, and it is the standard
language for the later predictive (data-science) extension.

### 3. NumPy
**What it is:** a library for fast, array-based numerical computing.
**Role here:** seeded random sampling for the simulation (`np.random.choice` with probability weights for device
tier; `np.random.normal` for time spent on a step) and numerical helpers (`np.where` to compute wasted fees).
**Why chosen:** vectorised operations and reproducible random streams via a fixed seed.

### 4. Pandas
**What it is:** a library providing the DataFrame, a labelled table structure with grouping, joining, reshaping.
**Role here:** cleaning and validation (null checks, duplicate checks, orphan-row check, type conversion), and
computing the Step-Metrics Matrix with `groupby`, `agg`, `merge`, `pd.cut` (Time-to-Abandon cohorts) and `unstack`.
**Why chosen:** it expresses "group by step, compute rate" in one line and integrates with Matplotlib/Seaborn.

### 5. Faker
**What it is:** a library that generates realistic fake values.
**Role here:** generates a fake, seeded 8-character `user_ref` for each session (a stand-in for a real user
identifier). *Honest note:* this is a deliberately small use. Device, region, document type and all outcomes come from
NumPy/`random`, not Faker. It is kept because it is the natural tool if names, emails or other identifiers are
added later; do not describe it as central to the project.

### 6. SQL and MySQL
**What it is:** SQL is the standard language for relational databases; MySQL is a widely used open-source engine.
**Role here:**
- **DDL:** `CREATE TABLE` with primary keys, a foreign key (`fact_events.session_id -> fact_user_sessions.session_id`)
  and indexes on the join/group columns.
- **Analysis:** aggregations (`COUNT(DISTINCT ...)`, conditional `CASE WHEN`), joins (error-impact query),
  and CTEs (`WITH`) for the Time-to-Abandon cohorts.
**Why MySQL:** the mentor's brief specifies it. **Why a database at all** for ~10k sessions: it demonstrates a
realistic pipeline (data at rest -> query -> analysis) and lets SQL do aggregation before Python.
**Honest note:** at this scale Pandas alone would suffice; the database is for workflow fidelity and to meet the brief.

**Two-table design.** `fact_user_sessions` (one row per session) is the outcome table and is shaped to serve as a
feature table plus target (`has_abandoned`) for a future predictive model. `fact_events` (one row per attempt)
carries step-level detail. Keeping them separate avoids repeating session attributes on every event row.

### 7. SQLAlchemy and mysql-connector-python
**What they are:** `mysql-connector-python` is Oracle's pure-Python MySQL driver; SQLAlchemy is a toolkit that
wraps drivers behind an "engine" and integrates with Pandas.
**Role here:** `db_connector.py` builds a connection URL (`mysql+mysqlconnector://user:pass@host:port/db`),
creates an engine, and exposes `run_query`, `load_sessions`, `load_events` returning DataFrames via `pd.read_sql`.
`load_to_mysql.py` uses `DataFrame.to_sql` for bulk inserts with `chunksize`.
**Security practice:** credentials are read from environment variables and never committed to Git.

### 8. Matplotlib and Seaborn
**What they are:** Matplotlib is the base plotting library; Seaborn adds statistical charts and defaults on top.
**Role here:** all notebook charts (funnel bars, stacked Time-to-Abandon bars, error-impact bars, device
failure heatmap). The mentor's brief requires these two libraries specifically.

### 9. Jupyter Notebook
**What it is:** an interactive document mixing code, output and narrative.
**Role here:** the analysis record: each finding sits next to the code that produced it, so it is reproducible.

### 10. Power BI
**What it is:** Microsoft's business-intelligence tool for interactive dashboards.
**Role here:** the stakeholder layer: KPI cards, funnel visual, slicers (device, document type, region),
drill-down from step to error type, conditional-formatted matrices, and a recommendations page.
**Key features used:** a small star-style model (fact tables joined to `dim_stage` and `dim_device`), **DAX
measures** for rates that must recalculate under slicers (e.g. `DIVIDE([Abandoned Sessions],[Total Sessions])`),
and **Sort by column** to keep funnel stages in order.
**Why chosen:** required by the brief and suited to non-technical audiences. **Limitation:** the delivered
dashboard is static (imported data), not a live feed.

### 11. Reproducibility and verification
- Random seed fixed (42), so every run produces identical data.
- SQL results and Pandas results were cross-checked: e.g. per-step drop-off (5.49 / 3.74 / 7.42 / 8.49 / 4.45 %)
  and device abandonment (40.11 / 26.56 / 19.57 %) match in both.
- Reference values are provided so the Power BI measures can be checked against them.

### 12. Tool choices considered but not used (and why)
- **Live/streaming stack (FastAPI, Supabase, Streamlit):** appropriate for a *dynamic* portfolio version;
  out of scope for a static, one-time analysis. Documented as future work.
- **Big-data tools (Kafka, Spark, warehouses):** unjustified at ~10k sessions; naming them would be overstating.

### References
1. Python Software Foundation. *Python 3 documentation*. https://docs.python.org/3/
2. NumPy. *NumPy documentation*. https://numpy.org/doc/stable/
3. pandas. *pandas documentation*. https://pandas.pydata.org/docs/
4. Matplotlib. *Matplotlib documentation*. https://matplotlib.org/stable/
5. seaborn. *seaborn documentation*. https://seaborn.pydata.org/
6. Oracle. *MySQL 8.0 Reference Manual* — CREATE TABLE and FOREIGN KEY Constraints. https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html
7. SQLAlchemy. *Engine Configuration* (Database URLs, `create_engine`). https://docs.sqlalchemy.org/en/20/core/engines.html
8. Oracle. *MySQL Connector/Python Developer Guide*. https://dev.mysql.com/doc/connector-python/en/
9. Microsoft. *Power BI documentation* — data modelling and DAX reference. https://learn.microsoft.com/en-us/power-bi/
10. Faker. *Faker documentation*. https://faker.readthedocs.io/en/stable/
