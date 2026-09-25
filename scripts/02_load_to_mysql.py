# Load the generated KYC data into MySQL

import pandas as pd
from sqlalchemy import text
from generate_data import generate_dataset
from db_connector import get_engine


# Generate the dataset and bulk-insert both MySQL tables
def main(engine=None):
    engine = engine or get_engine()
    events_df, sessions_df = generate_dataset()
    events_df = events_df.rename(columns={"timestamp": "event_time"})
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fact_events"))
        conn.execute(text("DELETE FROM fact_user_sessions"))
    sessions_df.to_sql("fact_user_sessions", engine, if_exists="append",
                       index=False, chunksize=2000)
    events_df.to_sql("fact_events", engine, if_exists="append",
                     index=False, chunksize=5000)
    with engine.connect() as conn:
        n_s = conn.execute(text("SELECT COUNT(*) FROM fact_user_sessions")).scalar()
        n_e = conn.execute(text("SELECT COUNT(*) FROM fact_events")).scalar()
    print(f"Loaded fact_user_sessions={n_s}, fact_events={n_e}")


# Run the loader when the script is executed directly
if __name__ == "__main__":
    main()
