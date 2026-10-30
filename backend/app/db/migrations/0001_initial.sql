BEGIN;

CREATE TABLE menu_items (
    id VARCHAR(36) PRIMARY KEY,
    menu_name VARCHAR(120) NOT NULL UNIQUE,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_temperatures JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_sizes JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_options JSONB NOT NULL DEFAULT '[]'::jsonb,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_requests (
    id VARCHAR(36) PRIMARY KEY,
    trace_id VARCHAR(36) NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    status VARCHAR(40) NOT NULL,
    state_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_order_state_version_positive CHECK (state_version >= 1)
);

CREATE TABLE normalized_orders (
    id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL REFERENCES order_requests(id) ON DELETE CASCADE,
    person_name VARCHAR(80) NOT NULL,
    source_text TEXT NOT NULL,
    menu_name VARCHAR(120) NOT NULL,
    temperature VARCHAR(20) NOT NULL,
    size VARCHAR(20) NOT NULL DEFAULT '톨',
    options JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_normalized_order_request_person UNIQUE (request_id, person_name)
);

CREATE INDEX ix_normalized_orders_request_id ON normalized_orders(request_id);

CREATE TABLE incidents (
    incident_id VARCHAR(36) PRIMARY KEY,
    trace_id VARCHAR(36) NOT NULL,
    agent VARCHAR(80) NOT NULL,
    failure_type VARCHAR(40) NOT NULL,
    status VARCHAR(40) NOT NULL,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    attempt INTEGER NOT NULL DEFAULT 1,
    requires_human_approval BOOLEAN NOT NULL DEFAULT FALSE,
    detected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_incident_attempt_range CHECK (attempt BETWEEN 1 AND 3)
);

CREATE INDEX ix_incidents_trace_id ON incidents(trace_id);

CREATE TABLE recovery_attempts (
    recovery_id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    attempt INTEGER NOT NULL,
    action VARCHAR(120) NOT NULL,
    result VARCHAR(40) NOT NULL,
    duration_ms INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    CONSTRAINT uq_recovery_incident_attempt UNIQUE (incident_id, attempt),
    CONSTRAINT ck_recovery_attempt_range CHECK (attempt BETWEEN 1 AND 3),
    CONSTRAINT ck_recovery_duration_nonnegative CHECK (duration_ms >= 0)
);

CREATE INDEX ix_recovery_attempts_incident_id ON recovery_attempts(incident_id);

COMMIT;
