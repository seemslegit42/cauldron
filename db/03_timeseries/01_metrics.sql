-- Time-series module - System and business metrics using TimescaleDB

-- System metrics table (hypertable)
CREATE TABLE timeseries.system_metrics (
    time TIMESTAMPTZ NOT NULL,
    host VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.system_metrics', 'time');

COMMENT ON TABLE timeseries.system_metrics IS 'System-level metrics collected over time';

-- User activity tracking (hypertable)
CREATE TABLE timeseries.user_activity (
    time TIMESTAMPTZ NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    activity_type VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.user_activity', 'time');

COMMENT ON TABLE timeseries.user_activity IS 'User activity and behavior tracking over time';

-- Business metrics (hypertable)
CREATE TABLE timeseries.business_metrics (
    time TIMESTAMPTZ NOT NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    dimensions JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.business_metrics', 'time');

COMMENT ON TABLE timeseries.business_metrics IS 'Business KPIs and metrics tracked over time';

-- Agent performance metrics (hypertable)
CREATE TABLE timeseries.agent_metrics (
    time TIMESTAMPTZ NOT NULL,
    agent_id UUID NOT NULL,
    execution_id UUID,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.agent_metrics', 'time');

COMMENT ON TABLE timeseries.agent_metrics IS 'AI agent performance metrics over time';

-- Create indexes for efficient querying
CREATE INDEX idx_system_metrics_metric_name ON timeseries.system_metrics (metric_name, time DESC);
CREATE INDEX idx_system_metrics_host ON timeseries.system_metrics (host, time DESC);
CREATE INDEX idx_system_metrics_tags ON timeseries.system_metrics USING GIN (tags);

CREATE INDEX idx_user_activity_user_id ON timeseries.user_activity (user_id, time DESC);
CREATE INDEX idx_user_activity_activity_type ON timeseries.user_activity (activity_type, time DESC);

CREATE INDEX idx_business_metrics_organization_id ON timeseries.business_metrics (organization_id, time DESC);
CREATE INDEX idx_business_metrics_metric_name ON timeseries.business_metrics (metric_name, time DESC);
CREATE INDEX idx_business_metrics_dimensions ON timeseries.business_metrics USING GIN (dimensions);

CREATE INDEX idx_agent_metrics_agent_id ON timeseries.agent_metrics (agent_id, time DESC);
CREATE INDEX idx_agent_metrics_execution_id ON timeseries.agent_metrics (execution_id, time DESC);
CREATE INDEX idx_agent_metrics_metric_name ON timeseries.agent_metrics (metric_name, time DESC);
CREATE INDEX idx_agent_metrics_tags ON timeseries.agent_metrics USING GIN (tags);

-- Create continuous aggregates for common queries
CREATE MATERIALIZED VIEW timeseries.hourly_system_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    host,
    metric_name,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value,
    COUNT(*) AS sample_count
FROM timeseries.system_metrics
GROUP BY bucket, host, metric_name;

CREATE MATERIALIZED VIEW timeseries.daily_business_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    organization_id,
    metric_name,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value,
    COUNT(*) AS sample_count
FROM timeseries.business_metrics
GROUP BY bucket, organization_id, metric_name;

-- Add retention policies (adjust retention periods as needed)
SELECT add_retention_policy('timeseries.system_metrics', INTERVAL '30 days');
SELECT add_retention_policy('timeseries.user_activity', INTERVAL '90 days');
SELECT add_retention_policy('timeseries.hourly_system_metrics', INTERVAL '365 days');
SELECT add_retention_policy('timeseries.daily_business_metrics', INTERVAL '730 days');

-- Create functions for common time-series operations
CREATE OR REPLACE FUNCTION timeseries.get_metric_trend(
    p_metric_name VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_interval INTERVAL DEFAULT '1 hour'::INTERVAL
)
RETURNS TABLE (
    bucket TIMESTAMPTZ,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    sample_count BIGINT
)
LANGUAGE SQL
AS $$
    SELECT
        time_bucket(p_interval, time) AS bucket,
        AVG(metric_value) AS avg_value,
        MIN(metric_value) AS min_value,
        MAX(metric_value) AS max_value,
        COUNT(*) AS sample_count
    FROM timeseries.system_metrics
    WHERE metric_name = p_metric_name
      AND time >= p_start_time
      AND time <= p_end_time
    GROUP BY bucket
    ORDER BY bucket;
$$;

COMMENT ON FUNCTION timeseries.get_metric_trend IS 'Get trend data for a specific metric over a time range';