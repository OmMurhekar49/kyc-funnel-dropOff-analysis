# Export the five CSV tables used by Power BI

import os
import pandas as pd
from db_connector import get_engine, run_query

# Set the project root and Power BI output folder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "powerbi", "data")
os.makedirs(OUT, exist_ok=True)

# Load the database tables and prepare the Power BI dimension tables
def main(eng=None):
    eng = eng or get_engine()
    sessions = run_query("SELECT * FROM fact_user_sessions", eng)
    events = run_query("SELECT * FROM fact_events", eng)

    dim_stage = pd.DataFrame({
        "stage": ["registration", "phone_otp", "doc_upload", "liveness_check", "consent_sign"],
        "stage_order": [1, 2, 3, 4, 5],
        "stage_label": ["1 Registration", "2 Phone OTP", "3 Doc Upload", "4 Liveness Check", "5 Consent Sign"],
    })
    dim_device = pd.DataFrame({
        "device_tier": ["iOS-HighEnd", "Android-MidTier", "Android-Budget"],
        "device_order": [1, 2, 3],
    })

    # Create the Time-to-Abandon cohorts and attach device information
    step_time = events.groupby(["session_id", "stage"]).time_on_step.sum().reset_index(name="step_seconds")
    quits = events[events.drop_off_flag == 1][["session_id", "stage"]].drop_duplicates()
    quits = quits.merge(step_time, on=["session_id", "stage"])
    quits["abandon_cohort"] = pd.cut(quits.step_seconds, [-1, 4, 60, 10**6],
                                     labels=["No-intent (<5s)", "Mid (5-60s)", "Blocker (60s+)"]).astype(str)
    quits = quits.merge(sessions[["session_id", "device_tier"]], on="session_id")

    # Export all five tables as CSV files
    for name, df in [("fact_user_sessions", sessions), ("fact_events", events), ("dim_stage", dim_stage),
                     ("dim_device", dim_device), ("fact_quit_points", quits)]:
        df.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
        print(f"wrote {name}.csv  ({len(df)} rows)")


# Run the export when the script is executed directly
if __name__ == "__main__":
    main()
