-- Time-series module - Event tracking and analysis

-- Event log table (hypertable)
CREATE TABLE timeseries.events (
    time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    entity_type VARCHAR(100),
    entity_id UUID,
    severity VARCHAR(20) DEFAULT 'info',
    details JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.events', 'time');

COMMENT ON TABLE timeseries.events IS 'System-wide event log for auditing and analysis';

-- Alerts table (hypertable)
CREATE TABLE timeseries.alerts (
    time TIMESTAMPTZ NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    title TEXT NOT NULL,
    description TEXT,
    entity_type VARCHAR(100),
    entity_id UUID,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES public.users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    resolution_notes TEXT,
    details JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.alerts', 'time');

COMMENT ON TABLE timeseries.alerts IS 'System alerts and notifications';

-- Anomaly detection table (hypertable)
CREATE TABLE timeseries.anomalies (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    expected_value DOUBLE PRECISION,
    actual_value DOUBLE PRECISION,
    deviation_percent DOUBLE PRECISION,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'detected',
    details JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.anomalies', 'time');

COMMENT ON TABLE timeseries.anomalies IS 'Detected anomalies in time-series data';

-- Create indexes for efficient querying
CREATE INDEX idx_events_event_type ON timeseries.events (event_type, time DESC);
CREATE INDEX idx_events_source ON timeseries.events (source, time DESC);
CREATE INDEX idx_events_user_id ON timeseries.events (user_id, time DESC);
CREATE INDEX idx_events_organization_id ON timeseries.events (organization_id, time DESC);
CREATE INDEX idx_events_entity ON timeseries.events (entity_type, entity_id, time DESC);
CREATE INDEX idx_events_severity ON timeseries.events (severity, time DESC);
CREATE INDEX idx_events_details ON timeseries.events USING GIN (details);
CREATE INDEX idx_events_metadata ON timeseries.events USING GIN (metadata);

CREATE INDEX idx_alerts_alert_type ON timeseries.alerts (alert_type, time DESC);
CREATE INDEX idx_alerts_source ON timeseries.alerts (source, time DESC);
CREATE INDEX idx_alerts_severity ON timeseries.alerts (severity, time DESC);
CREATE INDEX idx_alerts_status ON timeseries.alerts (status, time DESC);
CREATE INDEX idx_alerts_organization_id ON timeseries.alerts (organization_id, time DESC);
CREATE INDEX idx_alerts_assigned_to ON timeseries.alerts (assigned_to, time DESC);
CREATE INDEX idx_alerts_entity ON timeseries.alerts (entity_type, entity_id, time DESC);
CREATE INDEX idx_alerts_details ON timeseries.alerts USING GIN (details);

CREATE INDEX idx_anomalies_metric_name ON timeseries.anomalies (metric_name, time DESC);
CREATE INDEX idx_anomalies_entity ON timeseries.anomalies (entity_type, entity_id, time DESC);
CREATE INDEX idx_anomalies_severity ON timeseries.anomalies (severity, time DESC);
CREATE INDEX idx_anomalies_status ON timeseries.anomalies (status, time DESC);
CREATE INDEX idx_anomalies_details ON timeseries.anomalies USING GIN (details);

-- Create continuous aggregates for event analysis
CREATE MATERIALIZED VIEW timeseries.hourly_events
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    event_type,
    source,
    organization_id,
    COUNT(*) AS event_count
FROM timeseries.events
GROUP BY bucket, event_type, source, organization_id;

CREATE MATERIALIZED VIEW timeseries.daily_alerts
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    alert_type,
    severity,
    status,
    organization_id,
    COUNT(*) AS alert_count
FROM timeseries.alerts
GROUP BY bucket, alert_type, severity, status, organization_id;

-- Add retention policies
SELECT add_retention_policy('timeseries.events', INTERVAL '90 days');
SELECT add_retention_policy('timeseries.alerts', INTERVAL '365 days');
SELECT add_retention_policy('timeseries.anomalies', INTERVAL '180 days');
SELECT add_retention_policy('timeseries.hourly_events', INTERVAL '730 days');
SELECT add_retention_policy('timeseries.daily_alerts', INTERVAL '1825 days');

-- Create functions for event analysis
CREATE OR REPLACE FUNCTION timeseries.get_event_frequency(
    p_event_type VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_interval INTERVAL DEFAULT '1 hour'::INTERVAL,
    p_organization_id UUID DEFAULT NULL
)
RETURNS TABLE (
    bucket TIMESTAMPTZ,
    event_count BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        time_bucket(p_interval, time) AS bucket,
        COUNT(*) AS event_count
    FROM timeseries.events
    WHERE event_type = p_event_type
      AND time >= p_start_time
      AND time <= p_end_time
      AND (p_organization_id IS NULL OR organization_id = p_organization_id)
    GROUP BY bucket
    ORDER BY bucket;
$$;

COMMENT ON FUNCTION timeseries.get_event_frequency IS 'Get frequency of a specific event type over a time range';

-- Create function to log events
CREATE OR REPLACE FUNCTION timeseries.log_event(
    p_event_type VARCHAR,
    p_source VARCHAR,
    p_user_id UUID DEFAULT NULL,
    p_organization_id UUID DEFAULT NULL,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL,
    p_severity VARCHAR DEFAULT 'info',
    p_details JSONB DEFAULT '{}',
    p_metadata JSONB DEFAULT '{}'
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO timeseries.events (
        time,
        event_type,
        source,
        user_id,
        organization_id,
        entity_type,
        entity_id,
        severity,
        details,
        metadata
    ) VALUES (
        NOW(),
        p_event_type,
        p_source,
        p_user_id,
        p_organization_id,
        p_entity_type,
        p_entity_id,
        p_severity,
        p_details,
        p_metadata
    )
    RETURNING entity_id INTO v_id;
    
    RETURN v_id;
END;
$$;

COMMENT ON FUNCTION timeseries.log_event IS 'Log an event in the system';