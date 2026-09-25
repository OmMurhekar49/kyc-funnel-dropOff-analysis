-- PART 1 : TABLE CREATION

CREATE DATABASE IF NOT EXISTS kyc_funnel;
USE kyc_funnel;
DROP TABLE IF EXISTS fact_events;
DROP TABLE IF EXISTS fact_user_sessions;
CREATE TABLE fact_user_sessions (
    session_id               VARCHAR(10)  NOT NULL,
    user_ref                 VARCHAR(10)  NOT NULL,
    device_tier              VARCHAR(20)  NOT NULL,
    doc_type                 VARCHAR(20)  NOT NULL,
    region                   VARCHAR(20)  NOT NULL,
    document_upload_retries  INT          NOT NULL,
    biometric_error_count    INT          NOT NULL,
    total_error_count        INT          NOT NULL,
    total_duration_seconds   INT          NOT NULL,
    last_stage_reached       VARCHAR(20)  NOT NULL,
    total_vendor_cost        DECIMAL(8,2) NOT NULL,
    has_abandoned            TINYINT      NOT NULL,
    session_start            DATETIME     NOT NULL,
    PRIMARY KEY (session_id)
);
CREATE TABLE fact_events (
    event_id       INT          NOT NULL AUTO_INCREMENT,
    session_id     VARCHAR(10)  NOT NULL,
    stage          VARCHAR(20)  NOT NULL,
    event_time     DATETIME     NOT NULL,
    device_type    VARCHAR(20)  NOT NULL,
    error_type     VARCHAR(30)  NULL,
    retry_count    INT          NOT NULL,
    time_on_step   INT          NOT NULL,
    attempt_cost   DECIMAL(6,2) NOT NULL,
    drop_off_flag  TINYINT      NOT NULL,
    PRIMARY KEY (event_id),
    FOREIGN KEY (session_id) REFERENCES fact_user_sessions(session_id)
);
CREATE INDEX idx_events_session ON fact_events(session_id);
CREATE INDEX idx_events_stage   ON fact_events(stage);


---