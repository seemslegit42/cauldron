-- Enable required extensions for Cauldron sEOS
-- Run as superuser

-- Vector database extension for knowledge management
CREATE EXTENSION IF NOT EXISTS vector;

-- Time-series extension for metrics and monitoring
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- JSON functionality
CREATE EXTENSION IF NOT EXISTS jsonb_plpython3u;

-- Comment on database
COMMENT ON DATABASE current_database() IS 'Cauldron sEOS - Sentient Enterprise Operating System Database';
