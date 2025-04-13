-- Time-series module - Forecasting and predictive analytics

-- Forecast models table
CREATE TABLE timeseries.forecast_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    target_metric VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    parameters JSONB DEFAULT '{}',
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    accuracy_metrics JSONB DEFAULT '{}',
    last_trained_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE timeseries.forecast_models IS 'Time-series forecasting models';

-- Forecast data table (hypertable)
CREATE TABLE timeseries.forecasts (
    time TIMESTAMPTZ NOT NULL,
    model_id UUID NOT NULL REFERENCES timeseries.forecast_models(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    forecast_value DOUBLE PRECISION NOT NULL,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    prediction_interval DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.forecasts', 'time');

COMMENT ON TABLE timeseries.forecasts IS 'Time-series forecast predictions';

-- Seasonality patterns table
CREATE TABLE timeseries.seasonality_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    pattern_type VARCHAR(50) NOT NULL,
    period_length INTEGER NOT NULL,
    strength DOUBLE PRECISION,
    parameters JSONB DEFAULT '{}',
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE
);

COMMENT ON TABLE timeseries.seasonality_patterns IS 'Detected seasonality patterns in time-series data';

-- Trend analysis table
CREATE TABLE timeseries.trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    trend_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    slope DOUBLE PRECISION,
    intercept DOUBLE PRECISION,
    r_squared DOUBLE PRECISION,
    p_value DOUBLE PRECISION,
    significance VARCHAR(20),
    parameters JSONB DEFAULT '{}',
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE
);

COMMENT ON TABLE timeseries.trends IS 'Detected trends in time-series data';

-- Create indexes for efficient querying
CREATE INDEX idx_forecast_models_target_metric ON timeseries.forecast_models (target_metric);
CREATE INDEX idx_forecast_models_model_type ON timeseries.forecast_models (model_type);
CREATE INDEX idx_forecast_models_organization_id ON timeseries.forecast_models (organization_id);
CREATE INDEX idx_forecast_models_is_active ON timeseries.forecast_models (is_active);

CREATE INDEX idx_forecasts_model_id ON timeseries.forecasts (model_id, time DESC);
CREATE INDEX idx_forecasts_metric_name ON timeseries.forecasts (metric_name, time DESC);
CREATE INDEX idx_forecasts_entity ON timeseries.forecasts (entity_type, entity_id, time DESC);
CREATE INDEX idx_forecasts_is_anomaly ON timeseries.forecasts (is_anomaly, time DESC);
CREATE INDEX idx_forecasts_metadata ON timeseries.forecasts USING GIN (metadata);

CREATE INDEX idx_seasonality_patterns_metric_name ON timeseries.seasonality_patterns (metric_name);
CREATE INDEX idx_seasonality_patterns_entity ON timeseries.seasonality_patterns (entity_type, entity_id);
CREATE INDEX idx_seasonality_patterns_pattern_type ON timeseries.seasonality_patterns (pattern_type);
CREATE INDEX idx_seasonality_patterns_organization_id ON timeseries.seasonality_patterns (organization_id);

CREATE INDEX idx_trends_metric_name ON timeseries.trends (metric_name);
CREATE INDEX idx_trends_entity ON timeseries.trends (entity_type, entity_id);
CREATE INDEX idx_trends_trend_type ON timeseries.trends (trend_type);
CREATE INDEX idx_trends_significance ON timeseries.trends (significance);
CREATE INDEX idx_trends_organization_id ON timeseries.trends (organization_id);

-- Add retention policy
SELECT add_retention_policy('timeseries.forecasts', INTERVAL '365 days');

-- Create functions for forecasting
CREATE OR REPLACE FUNCTION timeseries.get_forecast(
    p_model_id UUID,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL
)
RETURNS TABLE (
    time TIMESTAMPTZ,
    forecast_value DOUBLE PRECISION,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    is_anomaly BOOLEAN
)
LANGUAGE SQL
AS $$
    SELECT
        time,
        forecast_value,
        confidence_lower,
        confidence_upper,
        is_anomaly
    FROM timeseries.forecasts
    WHERE model_id = p_model_id
      AND time >= p_start_time
      AND time <= p_end_time
      AND (p_entity_type IS NULL OR entity_type = p_entity_type)
      AND (p_entity_id IS NULL OR entity_id = p_entity_id)
    ORDER BY time;
$$;

COMMENT ON FUNCTION timeseries.get_forecast IS 'Get forecast data for a specific model and time range';

-- Create function to compare actual vs forecast
CREATE OR REPLACE FUNCTION timeseries.compare_actual_vs_forecast(
    p_metric_name VARCHAR,
    p_model_id UUID,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL,
    p_interval INTERVAL DEFAULT '1 hour'::INTERVAL
)
RETURNS TABLE (
    bucket TIMESTAMPTZ,
    actual_value DOUBLE PRECISION,
    forecast_value DOUBLE PRECISION,
    absolute_error DOUBLE PRECISION,
    percent_error DOUBLE PRECISION
)
LANGUAGE SQL
AS $$
    WITH actual_data AS (
        SELECT
            time_bucket(p_interval, time) AS bucket,
            AVG(metric_value) AS actual_value
        FROM timeseries.business_metrics
        WHERE metric_name = p_metric_name
          AND time >= p_start_time
          AND time <= p_end_time
          AND (p_entity_id IS NULL OR 
               (dimensions->>'entity_id')::UUID = p_entity_id AND
               (dimensions->>'entity_type')::VARCHAR = p_entity_type)
        GROUP BY bucket
    ),
    forecast_data AS (
        SELECT
            time_bucket(p_interval, time) AS bucket,
            AVG(forecast_value) AS forecast_value
        FROM timeseries.forecasts
        WHERE model_id = p_model_id
          AND time >= p_start_time
          AND time <= p_end_time
          AND (p_entity_type IS NULL OR entity_type = p_entity_type)
          AND (p_entity_id IS NULL OR entity_id = p_entity_id)
        GROUP BY bucket
    )
    SELECT
        a.bucket,
        a.actual_value,
        f.forecast_value,
        ABS(a.actual_value - f.forecast_value) AS absolute_error,
        CASE 
            WHEN a.actual_value = 0 THEN NULL
            ELSE ABS(a.actual_value - f.forecast_value) / a.actual_value * 100
        END AS percent_error
    FROM actual_data a
    JOIN forecast_data f ON a.bucket = f.bucket
    ORDER BY a.bucket;
$$;

COMMENT ON FUNCTION timeseries.compare_actual_vs_forecast IS 'Compare actual metrics with forecast predictions';

-- Create function to detect anomalies
CREATE OR REPLACE FUNCTION timeseries.detect_anomalies(
    p_metric_name VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_threshold DOUBLE PRECISION DEFAULT 3.0,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL
)
RETURNS TABLE (
    time TIMESTAMPTZ,
    actual_value DOUBLE PRECISION,
    expected_value DOUBLE PRECISION,
    deviation DOUBLE PRECISION,
    is_anomaly BOOLEAN
)
LANGUAGE SQL
AS $$
    WITH metric_stats AS (
        SELECT
            AVG(metric_value) AS avg_value,
            STDDEV(metric_value) AS stddev_value
        FROM timeseries.business_metrics
        WHERE metric_name = p_metric_name
          AND time >= p_start_time - INTERVAL '30 days'
          AND time < p_start_time
          AND (p_entity_id IS NULL OR 
               (dimensions->>'entity_id')::UUID = p_entity_id AND
               (dimensions->>'entity_type')::VARCHAR = p_entity_type)
    )
    SELECT
        m.time,
        m.metric_value AS actual_value,
        s.avg_value AS expected_value,
        ABS(m.metric_value - s.avg_value) / NULLIF(s.stddev_value, 0) AS deviation,
        ABS(m.metric_value - s.avg_value) / NULLIF(s.stddev_value, 0) > p_threshold AS is_anomaly
    FROM timeseries.business_metrics m
    CROSS JOIN metric_stats s
    WHERE m.metric_name = p_metric_name
      AND m.time >= p_start_time
      AND m.time <= p_end_time
      AND (p_entity_id IS NULL OR 
           (m.dimensions->>'entity_id')::UUID = p_entity_id AND
           (m.dimensions->>'entity_type')::VARCHAR = p_entity_type)
    ORDER BY m.time;
$$;

COMMENT ON FUNCTION timeseries.detect_anomalies IS 'Detect anomalies in time-series data using statistical methods';