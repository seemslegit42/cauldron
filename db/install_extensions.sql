-- Script to install required PostgreSQL extensions

-- Core extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS pg_trgm;         -- Full-text search
CREATE EXTENSION IF NOT EXISTS pgcrypto;        -- Cryptographic functions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements; -- Query performance monitoring

-- Vector database extension
CREATE EXTENSION IF NOT EXISTS vector;          -- PGVector for vector embeddings

-- Time-series extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE; -- TimescaleDB for time-series data

-- Optional extensions (if available)
DO $$
BEGIN
    -- Try to create each extension, but don't fail if not available
    BEGIN
        CREATE EXTENSION IF NOT EXISTS jsonb_plpython3u; -- JSON functionality
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension jsonb_plpython3u is not available, skipping...';
    END;

    BEGIN
        CREATE EXTENSION IF NOT EXISTS pgrouting; -- For graph operations
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension pgrouting is not available, skipping...';
    END;

    BEGIN
        CREATE EXTENSION IF NOT EXISTS postgis; -- Geospatial capabilities
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension postgis is not available, skipping...';
    END;

    BEGIN
        CREATE EXTENSION IF NOT EXISTS plpgsql_check; -- SQL code quality
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Extension plpgsql_check is not available, skipping...';
    END;
END
$$;