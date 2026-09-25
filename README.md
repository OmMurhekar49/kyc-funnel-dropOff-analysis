# KYC Funnel Drop-off Analysis (Digital Onboarding)

Where do users abandon a digital KYC / account-opening flow, why, and what does it cost?

> **Data is SIMULATED.** Real KYC data contains identity documents and biometrics and is not publicly available.
> The generator encodes documented rules (e.g. budget Android devices fail more on camera steps), so the analysis
> *recovers a designed pattern*. That validates the **method and pipeline**; it is not a claim about real users.

## Funnel
`registration -> phone_otp -> doc_upload -> liveness_check -> consent_sign`

## Approach: the Step-Metrics Matrix
| Dimension | Metric | Answers |
|---|---|---|
| Volume Velocity | Conversion and drop-off % | Where is the biggest leak? |
| Friction Density | Retries and errors per session | How hard is each step? |
| Time Dwell | Median duration, Time-to-Abandon | No-intent quitters or technical blockers? |

Plus Error-Impact Mapping, Device-Tier cohorts, and vendor-fee waste.

## Headline results (simulated, 10,000 sessions)
- Overall abandonment **26.35%**; biggest leak at **liveness check (8.49%)**, then document upload (7.42%)
- Early-step quitters are mostly **no-intent** (registration 94% leave in <5 s); camera-step quitters include a **60 s+ blocker** group (24% of doc-upload, 16% of liveness quitters)
- Abandonment by device: **Budget Android 40.1%**, Mid Android 26.6%, iOS 19.6%
- **$7,080 of $35,101 (20.2%)** of simulated vendor fees went to failed attempts; Budget Android is 19.4% of users but 41.3% of that waste
- If Budget Android matched Mid-Tier: about **263 sessions (2.6% of all, 10% of abandonment)** recovered
- Region and document type show **no meaningful differences** (none was built in) and no insight is claimed from them

## Repository layout
```text
scripts/
  01_generate_data.py            > batch simulator (seeded, reproducible)
  02_load_to_mysql.py            > bulk-insert into MySQL
  04_db_connector.py             > SQLAlchemy + mysql-connector-python -> DataFrames   [required .py]
  06_export_powerbi_data.py      > writes the 5 CSVs Power BI loads (powerbi/data/)

sql/
  03_1_create_tables.sql
  03_2_validation_and_analysis.sql

notebooks/
  05_kyc_funnel_analysis.ipynb                     > cleaning, EDA, all charts      [required .ipynb]

powerbi/
  kyc-funnel-dropOff-analysis-dashboards.pbix      > interactive dashboard           [required .pbix]
  kyc-funnel-dropOff-analysis-dashboards.pdf       > dashboard preview
  data/                                            > CSVs the dashboard loads

papers/
  Paper1_Domain_Research.md
  Paper2_Technology_Research.md

outputs/                                           > charts (PNG) and summary tables (CSV)
data/                                              > raw generator output (CSV)
```


### Execution order

#### 01 : Generates the simulated data
```powershell
python scripts\01_generate_data.py
```

#### 02 : Loads the data into MySQL
```powershell
python scripts\02_load_to_mysql.py
```

#### 03 : Runs the SQL table creation
Open and execute:
```text
sql\03_1_create_tables.sql
```

#### 03 : Runs the SQL validation and analysis
Open and execute:
```text
sql\03_2_validation_and_analysis.sql
```

#### 04 : Runs the Python database connector
```powershell
python scripts\04_db_connector.py
```

#### 05 : Runs the analysis notebook
Open:
```text
notebooks\05_kyc_funnel_analysis.ipynb
```

Running the notebook cells in order for data loading, cleaning, metric calculation, cohort analysis, and visualizations.

#### 06 : Exports data for Power BI
```powershell
python scripts\06_export_powerbi_data.py
```

#### 07 : Opens the Power BI dashboard
Open:
```text
powerbi\kyc-funnel-dropOff-analysis-dashboards.pbix
```

The running is **static and reproducible** (fixed seed), not a live pipeline.

## Limitations
Simulated data; independent-attempt assumption; observational (not causal); no fraud rejection or manual review;
assumed vendor fees. With real data the same pipeline applies, but the numbers would change.

## Future work (documented, not built)
Live/streaming version (FastAPI, Supabase/DuckDB, Streamlit); predictive abandonment model on the same session table
(Logistic Regression, then gradient boosting with SHAP); real-time nudges when predicted risk is high.
