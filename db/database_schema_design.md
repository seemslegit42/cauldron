# Comprehensive Database Schema Design

This document outlines a comprehensive database schema design incorporating PostgreSQL as the foundation with integrations for Supabase, vector database capabilities (PGVector), and time-series functionality (TimescaleDB).

## Core Architecture Components

### 1. PostgreSQL Foundation
- **Version**: PostgreSQL 15+ (recommended for optimal performance and feature support)
- **Extensions**: 
  - `pgvector` for vector embeddings and similarity search
  - `timescaledb` for time-series data management
  - `uuid-ossp` for UUID generation
  - `pg_trgm` for text search capabilities
  - `jsonb_plpython3u` for advanced JSON processing

### 2. Schema Organization
The database is organized into logical schemas to separate different functional areas:

#### Core Schemas
- **public**: Core tables for users, roles, permissions, organizations, and system settings
- **erp**: ERPNext core tables
- **hr**: HR module tables
- **crm**: CRM module tables

#### Module Schemas
- **command_cauldron**: AI Software Development & Autonomous DevOps
- **synapse**: Predictive & Prescriptive Business Intelligence
- **aegis**: Proactive & Autonomous Cybersecurity
- **lore**: Collective Intelligence & Knowledge Synthesis

#### Technical Schemas
- **vector**: Vector embeddings using PGVector
- **timeseries**: Time-series data using TimescaleDB
- **audit**: Audit and logging tables
- **admin**: Administrative functions and procedures
- **supabase**: Supabase integration tables and functions
- **auth**: Supabase Auth functionality
- **storage**: Supabase Storage functionality
- **realtime**: Supabase Realtime functionality
- **analytics**: Analytics and reporting
- **integration**: External system integrations

## Detailed Schema Design

### 1. Core User Management (public schema)

```sql
-- Users table
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(180) NOT NULL UNIQUE,
    email VARCHAR(180) NOT NULL UNIQUE,
    full_name VARCHAR(180) NOT NULL,
    hashed_password TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_system_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- User profile information
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    profile_image_url TEXT,
    job_title VARCHAR(180),
    department VARCHAR(180),
    bio TEXT,
    contact_email VARCHAR(180),
    phone VARCHAR(50),
    timezone VARCHAR(50),
    locale VARCHAR(10) DEFAULT 'en-US',
    theme VARCHAR(50) DEFAULT 'light',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Organizations table
CREATE TABLE public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    slug VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    logo_url TEXT,
    website TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organization memberships
CREATE TABLE public.organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles(id),
    is_owner BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- Teams within organizations
CREATE TABLE public.teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    name VARCHAR(180) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- Team memberships
CREATE TABLE public.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles(id),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);
```

### 2. Role-Based Access Control (public schema)

```sql
-- Roles table
CREATE TABLE public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permissions table
CREATE TABLE public.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(180) NOT NULL UNIQUE,
    name VARCHAR(180) NOT NULL,
    description TEXT,
    resource_type VARCHAR(180) NOT NULL,
    action VARCHAR(180) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(resource_type, action)
);

-- Role permissions
CREATE TABLE public.role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);
```

### 3. Vector Database (vector schema)

```sql
-- Embedding models table
CREATE TABLE vector.embedding_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(100) NOT NULL,
    dimensions INTEGER NOT NULL,
    version VARCHAR(50),
    description TEXT,
    configuration JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generic embeddings table
CREATE TABLE vector.embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    model VARCHAR(100) NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create HNSW index for fast similarity search
CREATE INDEX ON vector.embeddings USING hnsw (embedding vector_cosine_ops);

-- Collections for organizing embeddings
CREATE TABLE vector.collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    model_id UUID NOT NULL REFERENCES vector.embedding_models(id),
    metadata_schema JSONB DEFAULT '{}',
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Collection items
CREATE TABLE vector.collection_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL REFERENCES vector.collections(id) ON DELETE CASCADE,
    embedding_id UUID NOT NULL REFERENCES vector.embeddings(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(collection_id, embedding_id)
);
```

### 4. Time-Series Database (timeseries schema)

```sql
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

-- Business metrics (hypertable)
CREATE TABLE timeseries.business_metrics (
    time TIMESTAMPTZ DEFAULT NOW(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    dimensions JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.business_metrics', 'time');

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

-- Add retention policies
SELECT add_retention_policy('timeseries.system_metrics', INTERVAL '30 days');
SELECT add_retention_policy('timeseries.user_activity', INTERVAL '90 days');
SELECT add_retention_policy('timeseries.hourly_system_metrics', INTERVAL '365 days');
```

### 5. Supabase Integration (auth, storage, realtime schemas)

```sql
-- Supabase Auth users table
CREATE TABLE auth.users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    encrypted_password VARCHAR(255),
    email_confirmed_at TIMESTAMPTZ,
    phone_confirmed_at TIMESTAMPTZ,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMPTZ,
    email_change_token VARCHAR(255),
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB,
    raw_user_meta_data JSONB,
    is_super_admin BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_sso_user BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

-- Mapping between Supabase Auth users and application users
CREATE TABLE auth.user_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    app_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(auth_user_id),
    UNIQUE(app_user_id)
);

-- Supabase Storage buckets
CREATE TABLE storage.buckets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    public BOOLEAN DEFAULT FALSE
);

-- Supabase Storage objects
CREATE TABLE storage.objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id TEXT NOT NULL REFERENCES storage.buckets(id),
    name TEXT NOT NULL,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    path_tokens TEXT[] GENERATED ALWAYS AS (string_to_array(name, '/')) STORED,
    UNIQUE(bucket_id, name)
);
```

### 6. Knowledge Management (lore schema)

```sql
-- Documents table
CREATE TABLE lore.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text/plain',
    metadata JSONB DEFAULT '{}',
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    embedding_id UUID REFERENCES vector.embeddings(id) ON DELETE SET NULL
);

-- Document chunks for large documents
CREATE TABLE lore.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding_id UUID REFERENCES vector.embeddings(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Knowledge graph entities
CREATE TABLE lore.entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    embedding_id UUID REFERENCES vector.embeddings(id) ON DELETE SET NULL
);

-- Knowledge graph relationships
CREATE TABLE lore.relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    confidence FLOAT DEFAULT 1.0,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 7. AI Agent System (command_cauldron schema)

```sql
-- AI agents table
CREATE TABLE command_cauldron.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    agent_type VARCHAR(100) NOT NULL,
    configuration JSONB DEFAULT '{}',
    capabilities TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent executions
CREATE TABLE command_cauldron.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES command_cauldron.agents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    input JSONB DEFAULT '{}',
    output JSONB DEFAULT '{}',
    error TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    execution_time_ms INTEGER,
    metadata JSONB DEFAULT '{}'
);

-- Agent tools
CREATE TABLE command_cauldron.agent_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    tool_type VARCHAR(100) NOT NULL,
    configuration JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent tool assignments
CREATE TABLE command_cauldron.agent_tool_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES command_cauldron.agents(id) ON DELETE CASCADE,
    tool_id UUID NOT NULL REFERENCES command_cauldron.agent_tools(id) ON DELETE CASCADE,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_id, tool_id)
);
```

## Performance Optimizations

### 1. Indexing Strategy

```sql
-- Core table indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_organization_members_user_id ON public.organization_members(user_id);
CREATE INDEX idx_organization_members_organization_id ON public.organization_members(organization_id);
CREATE INDEX idx_team_members_user_id ON public.team_members(user_id);
CREATE INDEX idx_team_members_team_id ON public.team_members(team_id);

-- Vector indexes
CREATE INDEX ON vector.embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_embeddings_entity ON vector.embeddings (entity_type, entity_id);
CREATE INDEX idx_embeddings_model ON vector.embeddings (model);
CREATE INDEX idx_embeddings_metadata ON vector.embeddings USING GIN (metadata);

-- Time-series indexes
CREATE INDEX idx_system_metrics_metric_name ON timeseries.system_metrics (metric_name, time DESC);
CREATE INDEX idx_system_metrics_host ON timeseries.system_metrics (host, time DESC);
CREATE INDEX idx_system_metrics_tags ON timeseries.system_metrics USING GIN (tags);
CREATE INDEX idx_business_metrics_organization_id ON timeseries.business_metrics (organization_id, time DESC);
CREATE INDEX idx_business_metrics_metric_name ON timeseries.business_metrics (metric_name, time DESC);

-- Knowledge management indexes
CREATE INDEX idx_documents_organization_id ON lore.documents (organization_id);
CREATE INDEX idx_documents_created_by ON lore.documents (created_by);
CREATE INDEX idx_documents_metadata ON lore.documents USING GIN (metadata);
CREATE INDEX idx_document_chunks_document_id ON lore.document_chunks (document_id);
CREATE INDEX idx_entities_organization_id ON lore.entities (organization_id);
CREATE INDEX idx_entities_entity_type ON lore.entities (entity_type);
CREATE INDEX idx_relationships_source_id ON lore.relationships (source_id);
CREATE INDEX idx_relationships_target_id ON lore.relationships (target_id);
CREATE INDEX idx_relationships_relationship_type ON lore.relationships (relationship_type);

-- Full-text search indexes
CREATE INDEX idx_documents_content_trgm ON lore.documents USING GIN (content gin_trgm_ops);
CREATE INDEX idx_documents_title_trgm ON lore.documents USING GIN (title gin_trgm_ops);
```

### 2. Partitioning Strategy

```sql
-- Time-series data is automatically partitioned by TimescaleDB
-- Additional partitioning for large tables

-- Partition audit logs by month
CREATE TABLE audit.audit_logs (
    id UUID NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT
) PARTITION BY RANGE (time);

-- Create monthly partitions
CREATE TABLE audit.audit_logs_y2023m01 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE audit.audit_logs_y2023m02 PARTITION OF audit.audit_logs
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
-- Additional partitions would be created automatically by a maintenance process
```

### 3. Row-Level Security for Multi-Tenancy

```sql
-- Enable row-level security
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE lore.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector.collections ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY organization_member_access ON public.organizations
    USING (id IN (
        SELECT organization_id FROM public.organization_members
        WHERE user_id = current_user_id()
    ));

CREATE POLICY document_organization_access ON lore.documents
    USING (organization_id IN (
        SELECT organization_id FROM public.organization_members
        WHERE user_id = current_user_id()
    ));

-- Function to get current user ID
CREATE OR REPLACE FUNCTION public.current_user_id()
RETURNS UUID
LANGUAGE SQL SECURITY DEFINER
AS $$
    SELECT id FROM public.users WHERE username = current_user
$$;
```

## Integration Points

### 1. Supabase Integration

```sql
-- Trigger to sync Supabase Auth users to application users
CREATE OR REPLACE FUNCTION auth.sync_user_from_auth()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_app_user_id UUID;
    v_username VARCHAR;
    v_full_name VARCHAR;
BEGIN
    -- Extract username from email (before @)
    v_username := split_part(NEW.email, '@', 1);
    
    -- Extract full name from user metadata if available
    v_full_name := NEW.raw_user_meta_data->>'full_name';
    IF v_full_name IS NULL THEN
        v_full_name := v_username;
    END IF;
    
    -- Check if user already exists in application
    SELECT app_user_id INTO v_app_user_id
    FROM auth.user_mappings
    WHERE auth_user_id = NEW.id;
    
    IF v_app_user_id IS NULL THEN
        -- Create new application user
        INSERT INTO public.users (
            username,
            email,
            full_name,
            hashed_password,
            salt,
            is_active,
            created_at,
            modified_at,
            last_login
        ) VALUES (
            v_username,
            NEW.email,
            v_full_name,
            'SUPABASE_AUTH', -- Placeholder as auth is handled by Supabase
            'SUPABASE_AUTH', -- Placeholder as auth is handled by Supabase
            TRUE,
            NEW.created_at,
            NEW.updated_at,
            NEW.last_sign_in_at
        )
        RETURNING id INTO v_app_user_id;
        
        -- Create mapping
        INSERT INTO auth.user_mappings (auth_user_id, app_user_id)
        VALUES (NEW.id, v_app_user_id);
    ELSE
        -- Update existing application user
        UPDATE public.users
        SET
            email = NEW.email,
            full_name = v_full_name,
            is_active = (NEW.deleted_at IS NULL),
            modified_at = NEW.updated_at,
            last_login = NEW.last_sign_in_at
        WHERE id = v_app_user_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create trigger to sync users
CREATE TRIGGER trg_sync_user_from_auth
AFTER INSERT OR UPDATE ON auth.users
FOR EACH ROW
EXECUTE FUNCTION auth.sync_user_from_auth();
```

### 2. Vector Database Integration

```sql
-- Function to add document with automatic embedding
CREATE OR REPLACE FUNCTION lore.add_document_with_embedding(
    p_title VARCHAR,
    p_content TEXT,
    p_content_type VARCHAR,
    p_metadata JSONB,
    p_organization_id UUID,
    p_user_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_document_id UUID;
    v_embedding_id UUID;
BEGIN
    -- Create document
    INSERT INTO lore.documents (
        title,
        content,
        content_type,
        metadata,
        organization_id,
        created_by
    ) VALUES (
        p_title,
        p_content,
        p_content_type,
        p_metadata,
        p_organization_id,
        p_user_id
    ) RETURNING id INTO v_document_id;
    
    -- Create embedding
    SELECT vector.add_embedding(
        p_content,
        'document',
        v_document_id,
        NULL, -- Use default model
        jsonb_build_object('title', p_title, 'metadata', p_metadata)
    ) INTO v_embedding_id;
    
    -- Update document with embedding ID
    UPDATE lore.documents
    SET embedding_id = v_embedding_id
    WHERE id = v_document_id;
    
    RETURN v_document_id;
END;
$$;
```

### 3. Time-Series Integration

```sql
-- Function to record business metric
CREATE OR REPLACE FUNCTION timeseries.record_business_metric(
    p_organization_id UUID,
    p_metric_name VARCHAR,
    p_metric_value DOUBLE PRECISION,
    p_dimensions JSONB DEFAULT '{}'
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO timeseries.business_metrics (
        time,
        organization_id,
        metric_name,
        metric_value,
        dimensions
    ) VALUES (
        NOW(),
        p_organization_id,
        p_metric_name,
        p_metric_value,
        p_dimensions
    );
END;
$$;
```

## Setup and Maintenance

### 1. Database Creation Script

```sql
-- Create database
CREATE DATABASE cauldron_seos
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to database
\c cauldron_seos

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS jsonb_plpython3u;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS timeseries;
CREATE SCHEMA IF NOT EXISTS lore;
CREATE SCHEMA IF NOT EXISTS command_cauldron;
CREATE SCHEMA IF NOT EXISTS synapse;
CREATE SCHEMA IF NOT EXISTS aegis;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS admin;
```

### 2. Backup and Recovery

```sql
-- Enable WAL archiving in postgresql.conf
-- wal_level = replica
-- archive_mode = on
-- archive_command = 'cp %p /path/to/archive/%f'

-- Create backup function
CREATE OR REPLACE FUNCTION admin.create_backup(p_backup_path TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM pg_start_backup('Cauldron sEOS Backup');
    -- External script would copy files
    PERFORM pg_stop_backup();
END;
$$;

-- Create restore function
CREATE OR REPLACE FUNCTION admin.restore_from_backup(p_backup_path TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- External script would handle restore
    RAISE NOTICE 'Restore process must be handled externally';
END;
$$;
```

## Conclusion

This comprehensive database schema design provides a solid foundation for a modern enterprise application with:

1. **Robust relational data** using PostgreSQL's core capabilities
2. **Vector search capabilities** using PGVector for semantic search and AI features
3. **Efficient time-series storage** using TimescaleDB for metrics and events
4. **Authentication and storage** integration with Supabase
5. **Multi-tenant security** using row-level security policies
6. **Performance optimizations** through strategic indexing and partitioning
7. **Extensibility** through a modular schema design

The schema is designed to be scalable, maintainable, and adaptable to changing requirements while providing the performance needed for enterprise applications.