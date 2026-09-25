# Database connection script

import os
import getpass
import pandas as pd
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import URL

# Database connection settings
DB_USER = os.getenv("KYC_DB_USER", "root")
DB_HOST = os.getenv("KYC_DB_HOST", "localhost")
DB_PORT = int(os.getenv("KYC_DB_PORT", "3306"))
DB_NAME = os.getenv("KYC_DB_NAME", "kyc_funnel")

# Reuse the engine and password during the current run
_engine = None
_password = None

# Get the database password once
def _get_password():
    global _password
    if _password is None:
        env_pw = os.getenv("KYC_DB_PASS")
        _password = env_pw if env_pw is not None else getpass.getpass(f"MySQL password for user '{DB_USER}': ")
    return _password

# Create and test the shared database engine
def get_engine():
    global _engine
    if _engine is None:
        url = URL.create(drivername="mysql+mysqlconnector",
                         username=DB_USER, password=_get_password(),
                         host=DB_HOST, port=DB_PORT, database=DB_NAME)
        engine = create_engine(url)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as err:
            reason = str(getattr(err, "orig", err)).splitlines()[0]
            sys.exit(f"\nCould not connect to MySQL: {reason}\n"
                     "Check: (1) password typed correctly, (2) MySQL service running, "
                     "(3) database created via sql\\01_create_tables.sql")
        _engine = engine
    return _engine

# Run a SQL file against the MySQL server
def run_sql_file(path):
    url = URL.create(drivername="mysql+mysqlconnector", username=DB_USER, password=_get_password(),
                     host=DB_HOST, port=DB_PORT)
    server = create_engine(url)
    with open(path, encoding="utf-8") as f:
        script = f.read()
    lines = [l for l in script.splitlines() if not l.strip().startswith("--")]
    statements = [x.strip() for x in "\n".join(lines).split(";") if x.strip()]
    try:
        with server.begin() as conn:
            for stmt in statements:
                conn.exec_driver_sql(stmt)
    except SQLAlchemyError as err:
        reason = str(getattr(err, "orig", err)).splitlines()[0]
        sys.exit(f"\nCould not run {os.path.basename(path)}: {reason}")
    server.dispose()

# Run a query and return the result as a DataFrame
def run_query(sql, engine=None):
    engine = engine or get_engine()
    return pd.read_sql(sql, engine)

# Load session-level data
def load_sessions(engine=None):
    return run_query("SELECT * FROM fact_user_sessions", engine)

# Load event-level data
def load_events(engine=None):
    return run_query("SELECT * FROM fact_events", engine)

# Test the connection and data loading when the script is run directly
if __name__ == "__main__":
    eng = get_engine()
    s = load_sessions(eng)
    e = load_events(eng)
    print(f"Connected OK -> sessions: {s.shape}, events: {e.shape}")
