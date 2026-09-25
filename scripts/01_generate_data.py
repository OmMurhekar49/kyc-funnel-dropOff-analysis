# Batch generator for the simulated KYC funnel

# The dataset is simulated, with higher camera-step failure rates on budget Android devices

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker

# Set seeds and initialize Faker for reproducible data
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

# Set the simulation size and abandonment rules
N_SESSIONS = 10000
MAX_RETRIES = 3
ABANDON_AFTER_FAIL_PROB = 0.80
QUIT_AFTER_SINGLE_FAIL = {"registration": 0.10, "phone_otp": 0.14, "doc_upload": 0.22,
                          "liveness_check": 0.26, "consent_sign": 0.12}
NO_INTENT_QUIT = {"registration": 0.05, "phone_otp": 0.03, "doc_upload": 0.02,
                  "liveness_check": 0.01, "consent_sign": 0.04}
COST_PER_ATTEMPT = {"doc_upload": 1.50, "liveness_check": 2.00}

# Define the funnel steps and device distribution
STEPS = ["registration", "phone_otp", "doc_upload",
         "liveness_check", "consent_sign"]

DEVICE_TIERS = ["iOS-HighEnd", "Android-MidTier", "Android-Budget"]
DEVICE_WEIGHTS = [0.4, 0.4, 0.2]

# Define failure probabilities by device tier and funnel step
FAIL_CHANCE = {
    "iOS-HighEnd":     {"registration": 0.03, "phone_otp": 0.05, "doc_upload": 0.10, "liveness_check": 0.10, "consent_sign": 0.04},
    "Android-MidTier": {"registration": 0.04, "phone_otp": 0.07, "doc_upload": 0.18, "liveness_check": 0.20, "consent_sign": 0.05},
    "Android-Budget":  {"registration": 0.05, "phone_otp": 0.09, "doc_upload": 0.38, "liveness_check": 0.42, "consent_sign": 0.06},
}

# Define the error codes, timing assumptions, documents, and regions
STEP_ERRORS = {
    "registration":   ["ERR_TIMEOUT"],
    "phone_otp":      ["ERR_TIMEOUT"],
    "doc_upload":     ["ERR_GLARE_DETECTED", "ERR_BLURRY_DOC", "ERR_TIMEOUT"],
    "liveness_check": ["ERR_FACE_NOT_FOUND", "ERR_TIMEOUT"],
    "consent_sign":   ["ERR_TIMEOUT"],
}

BASE_SECONDS = {"registration": 25, "phone_otp": 20, "doc_upload": 45,
                "liveness_check": 30, "consent_sign": 15}
DOC_TYPES = ["Aadhaar", "PAN", "Passport", "Driving License"]
REGIONS = ["Maharashtra", "Karnataka", "Delhi",
           "Tamil Nadu", "Gujarat", "West Bengal"]


# Simulate one user's funnel journey
def generate_user_journey(session_id, start_time):
    device = str(np.random.choice(DEVICE_TIERS, p=DEVICE_WEIGHTS))
    doc_type = random.choice(DOC_TYPES)
    region = random.choice(REGIONS)
    events = []
    clock = start_time
    doc_retries = 0
    bio_errors = 0
    total_errors = 0
    total_cost = 0.0
    abandoned = 0
    last_step = STEPS[0]

    # Process each funnel step with bounded retries and abandonment rules
    for step in STEPS:
        step_done = False
        attempts = 0
        if random.random() < NO_INTENT_QUIT[step]:
            clock += timedelta(seconds=random.randint(1, 4))
            last_step = step
            events.append({"session_id": session_id, "stage": step, "timestamp": clock, "device_type": device,
                           "error_type": None, "retry_count": 0, "time_on_step": int((clock - events[-1]["timestamp"]).total_seconds()) if events else 3,
                           "attempt_cost": 0.0, "drop_off_flag": 1})
            abandoned = 1
            break
        while attempts < MAX_RETRIES and not step_done:
            attempts += 1
            duration = max(3, int(np.random.normal(BASE_SECONDS[step], BASE_SECONDS[step] * 0.3)))
            failed = random.random() < FAIL_CHANCE[device][step]
            error = random.choice(STEP_ERRORS[step]) if failed else None
            cost = COST_PER_ATTEMPT.get(step, 0.0)
            total_cost += cost
            clock += timedelta(seconds=duration)
            last_step = step
            events.append({
                "session_id": session_id,
                "stage": step,
                "timestamp": clock,
                "device_type": device,
                "error_type": error,
                "retry_count": attempts - 1,
                "time_on_step": duration,
                "attempt_cost": cost,
                "drop_off_flag": 0,
            })
            if failed:
                total_errors += 1
                last_fail_error = error
                if step == "liveness_check":
                    bio_errors += 1
                if step == "doc_upload":
                    doc_retries += 1
                if random.random() < QUIT_AFTER_SINGLE_FAIL[step]:
                    abandoned = 1
                    events[-1]["drop_off_flag"] = 1
                    break
            else:
                step_done = True

        if abandoned:
            break
        if not step_done:
            if random.random() < ABANDON_AFTER_FAIL_PROB:
                abandoned = 1
                events[-1]["drop_off_flag"] = 1
                break
            step_done = True

    # Build the session-level summary
    total_duration = int((clock - start_time).total_seconds())
    session = {
        "session_id": session_id,
        "user_ref": fake.uuid4()[:8].upper(),
        "device_tier": device,
        "doc_type": doc_type,
        "region": region,
        "document_upload_retries": doc_retries,
        "biometric_error_count": bio_errors,
        "total_error_count": total_errors,
        "total_duration_seconds": total_duration,
        "last_stage_reached": last_step,
        "total_vendor_cost": round(total_cost, 2),
        "has_abandoned": abandoned,
        "session_start": start_time,
    }
    return events, session


# Generate the full dataset in batch
def generate_dataset(n=N_SESSIONS):
    all_events, all_sessions = [], []
    base = datetime(2026, 1, 1, 8, 0, 0)
    for i in range(1, n + 1):
        start = base + timedelta(minutes=random.randint(0, 60 * 24 * 60))
        ev, se = generate_user_journey(f"S{i:06d}", start)
        all_events.extend(ev)
        all_sessions.append(se)
    return pd.DataFrame(all_events), pd.DataFrame(all_sessions)


# Generate and save the dataset when the script is executed directly
if __name__ == "__main__":
    events_df, sessions_df = generate_dataset()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    events_df.to_csv(os.path.join(root, "data", "kyc_events.csv"), index=False)
    sessions_df.to_csv(os.path.join(root, "data", "kyc_sessions.csv"), index=False)
    rate = sessions_df.has_abandoned.mean()
    print(f"Sessions: {len(sessions_df)} | Events: {len(events_df)} | Abandon rate: {rate:.1%}")
