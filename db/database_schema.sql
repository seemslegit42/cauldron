-- Cauldron sEOS Database Schema
-- Comprehensive schema incorporating PostgreSQL, Supabase, Vector Database, and Time-Series capabilities

-- =============================================
-- INITIALIZATION
-- =============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;          -- PGVector for vector embeddings
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE; -- TimescaleDB for time-series data
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS pg_trgm;         -- Full-text search
CREATE EXTENSION IF NOT EXISTS jsonb_plpython3u; -- JSON functionality
CREATE EXTENSION IF NOT EXISTS pgcrypto;        -- Cryptographic functions
CREATE EXTENSION IF NOT EXISTS pgrouting;       -- For graph operations
CREATE EXTENSION IF NOT EXISTS postgis;         -- Geospatial capabilities
CREATE EXTENSION IF NOT EXISTS plpgsql_check;   -- SQL code quality
CREATE EXTENSION IF NOT EXISTS pg_stat_statements; -- Query performance monitoring

-- Comment on database
COMMENT ON DATABASE current_database() IS 'Cauldron sEOS - Sentient Enterprise Operating System Database';

-- =============================================
-- SCHEMAS
-- =============================================

-- Default schema for shared tables (public schema already exists)

-- Core business modules
CREATE SCHEMA IF NOT EXISTS erp;
COMMENT ON SCHEMA erp IS 'ERPNext core tables';

CREATE SCHEMA IF NOT EXISTS hr;
COMMENT ON SCHEMA hr IS 'HR module tables';

CREATE SCHEMA IF NOT EXISTS crm;
COMMENT ON SCHEMA crm IS 'CRM module tables';

-- Cauldron sEOS modules
CREATE SCHEMA IF NOT EXISTS command_cauldron;
COMMENT ON SCHEMA command_cauldron IS 'Command & Cauldron module tables for AI Software Development & Autonomous DevOps';

CREATE SCHEMA IF NOT EXISTS synapse;
COMMENT ON SCHEMA synapse IS 'Synapse module tables for Predictive & Prescriptive Business Intelligence';

CREATE SCHEMA IF NOT EXISTS aegis;
COMMENT ON SCHEMA aegis IS 'Aegis Protocol module tables for Proactive & Autonomous Cybersecurity';

CREATE SCHEMA IF NOT EXISTS lore;
COMMENT ON SCHEMA lore IS 'Lore module tables for Collective Intelligence & Knowledge Synthesis';

-- Technical schemas
CREATE SCHEMA IF NOT EXISTS vector;
COMMENT ON SCHEMA vector IS 'Vector embeddings using PGVector';

CREATE SCHEMA IF NOT EXISTS timeseries;
COMMENT ON SCHEMA timeseries IS 'Time-series data using TimescaleDB';

CREATE SCHEMA IF NOT EXISTS audit;
COMMENT ON SCHEMA audit IS 'Audit and logging tables';

CREATE SCHEMA IF NOT EXISTS admin;
COMMENT ON SCHEMA admin IS 'Administrative functions and procedures';

CREATE SCHEMA IF NOT EXISTS supabase;
COMMENT ON SCHEMA supabase IS 'Supabase integration tables and functions';

CREATE SCHEMA IF NOT EXISTS realtime;
COMMENT ON SCHEMA realtime IS 'Supabase Realtime functionality';

CREATE SCHEMA IF NOT EXISTS storage;
COMMENT ON SCHEMA storage IS 'Supabase Storage functionality';

CREATE SCHEMA IF NOT EXISTS auth;
COMMENT ON SCHEMA auth IS 'Supabase Auth functionality';

CREATE SCHEMA IF NOT EXISTS analytics;
COMMENT ON SCHEMA analytics IS 'Analytics and reporting';

CREATE SCHEMA IF NOT EXISTS integration;
COMMENT ON SCHEMA integration IS 'External system integrations';

-- =============================================
-- CORE TABLES
-- =============================================

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

COMMENT ON TABLE public.users IS 'Core user accounts for the Cauldron sEOS platform';

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

COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';

-- User sessions
CREATE TABLE public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.user_sessions IS 'Active user sessions';

-- API tokens
CREATE TABLE public.api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token_name VARCHAR(180) NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    scopes TEXT[] DEFAULT '{}',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

COMMENT ON TABLE public.api_tokens IS 'API tokens for programmatic access';

-- Roles
CREATE TABLE public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.roles IS 'User roles for access control';

-- User-role assignments
CREATE TABLE public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

COMMENT ON TABLE public.user_roles IS 'Mapping between users and their assigned roles';

-- Permissions
CREATE TABLE public.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    module VARCHAR(180) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.permissions IS 'Available permissions in the system';

-- Role-permission assignments
CREATE TABLE public.role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

COMMENT ON TABLE public.role_permissions IS 'Mapping between roles and their assigned permissions';

-- Organizations
CREATE TABLE public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    domain VARCHAR(180),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.organizations IS 'Organizations using the Cauldron sEOS platform';

-- Teams
CREATE TABLE public.teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

COMMENT ON TABLE public.teams IS 'Teams within organizations';

-- Team members
CREATE TABLE public.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

COMMENT ON TABLE public.team_members IS 'Users belonging to teams';

-- Organization users
CREATE TABLE public.organization_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    is_owner BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

COMMENT ON TABLE public.organization_users IS 'Users belonging to organizations';

-- Organization invitations
CREATE TABLE public.organization_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    email VARCHAR(180) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    invited_by UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, email)
);

COMMENT ON TABLE public.organization_invitations IS 'Pending invitations to join organizations';

-- Audit logs
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.audit_logs IS 'System-wide audit trail of user actions';

-- System settings
CREATE TABLE public.system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(180) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.system_settings IS 'Global system configuration settings';

-- Organization settings
CREATE TABLE public.organization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    key VARCHAR(180) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, key)
);

COMMENT ON TABLE public.organization_settings IS 'Organization-specific configuration settings';

-- User settings
CREATE TABLE public.user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    key VARCHAR(180) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, key)
);

COMMENT ON TABLE public.user_settings IS 'User-specific configuration settings';

-- Schema migrations
CREATE TABLE public.schema_migrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    applied_by VARCHAR(100)
);

COMMENT ON TABLE public.schema_migrations IS 'Database schema version tracking';

-- =============================================
-- LORE MODULE (VECTOR DATABASE)
-- =============================================

-- Knowledge documents
CREATE TABLE lore.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    source_type VARCHAR(50),
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE lore.documents IS 'Knowledge documents in the Lore module';

-- Document chunks for embedding
CREATE TABLE lore.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536), -- Dimension depends on embedding model
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

COMMENT ON TABLE lore.document_chunks IS 'Chunked documents with vector embeddings for semantic search';

-- Document categories
CREATE TABLE lore.document_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES lore.document_categories(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.document_categories IS 'Categories for organizing documents';

-- Document-category associations
CREATE TABLE lore.document_category_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES lore.document_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, category_id)
);

COMMENT ON TABLE lore.document_category_associations IS 'Mapping between documents and categories';

-- Document tags
CREATE TABLE lore.document_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.document_tags IS 'Tags for documents';

-- Document-tag associations
CREATE TABLE lore.document_tag_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES lore.document_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, tag_id)
);

COMMENT ON TABLE lore.document_tag_associations IS 'Mapping between documents and tags';

-- Document teams (for access control)
CREATE TABLE lore.document_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, team_id)
);

COMMENT ON TABLE lore.document_teams IS 'Teams with access to specific documents';

-- Document versions
CREATE TABLE lore.document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

COMMENT ON TABLE lore.document_versions IS 'Historical versions of documents';

-- Knowledge graph entities
CREATE TABLE lore.entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entities IS 'Entities in the knowledge graph';

-- Knowledge graph relationships
CREATE TABLE lore.relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.relationships IS 'Relationships between entities in the knowledge graph';

-- Entity types
CREATE TABLE lore.entity_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entity_types IS 'Types of entities in the knowledge graph';

-- Relationship types
CREATE TABLE lore.relationship_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    source_types TEXT[] DEFAULT '{}',
    target_types TEXT[] DEFAULT '{}',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.relationship_types IS 'Types of relationships in the knowledge graph';

-- Entity-document associations
CREATE TABLE lore.entity_document_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_id, document_id)
);

COMMENT ON TABLE lore.entity_document_associations IS 'Mapping between entities and their source documents';

-- Entity mentions in documents
CREATE TABLE lore.entity_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL REFERENCES lore.entities(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES lore.documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES lore.document_chunks(id) ON DELETE CASCADE,
    start_offset INTEGER,
    end_offset INTEGER,
    mention_text TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.entity_mentions IS 'Specific mentions of entities within documents';

-- Semantic search queries
CREATE TABLE lore.search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    embedding VECTOR(1536),
    filters JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE lore.search_queries IS 'History of semantic search queries';

-- Search results
CREATE TABLE lore.search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES lore.search_queries(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES lore.document_chunks(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    rank INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(query_id, chunk_id)
);

COMMENT ON TABLE lore.search_results IS 'Results from semantic searches';

-- =============================================
-- TIMESERIES MODULE
-- =============================================

-- System metrics
CREATE TABLE timeseries.system_metrics (
    time TIMESTAMPTZ NOT NULL,
    host VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.system_metrics', 'time');

COMMENT ON TABLE timeseries.system_metrics IS 'System performance metrics';

-- User activity
CREATE TABLE timeseries.user_activity (
    time TIMESTAMPTZ NOT NULL,
    user_id UUID NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.user_activity', 'time');

COMMENT ON TABLE timeseries.user_activity IS 'User activity tracking';

-- Business metrics
CREATE TABLE timeseries.business_metrics (
    time TIMESTAMPTZ NOT NULL,
    organization_id UUID NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    dimensions JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.business_metrics', 'time');

COMMENT ON TABLE timeseries.business_metrics IS 'Business KPIs and metrics';

-- Agent execution metrics
CREATE TABLE timeseries.agent_metrics (
    time TIMESTAMPTZ NOT NULL,
    agent_id UUID NOT NULL,
    execution_id UUID NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('timeseries.agent_metrics', 'time');

COMMENT ON TABLE timeseries.agent_metrics IS 'AI agent performance metrics';

-- Continuous aggregates for common queries
CREATE MATERIALIZED VIEW timeseries.hourly_system_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    host,
    metric_name,
    AVG(metric_value) AS avg_value,
    MIN(metric_value) AS min_value,
    MAX(metric_value) AS max_value
FROM timeseries.system_metrics
GROUP BY bucket, host, metric_name;

-- Refresh policy
SELECT add_continuous_aggregate_policy('timeseries.hourly_system_metrics',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Daily user activity summary
CREATE MATERIALIZED VIEW timeseries.daily_user_activity
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    user_id,
    activity_type,
    COUNT(*) AS activity_count
FROM timeseries.user_activity
GROUP BY bucket, user_id, activity_type;

-- Refresh policy
SELECT add_continuous_aggregate_policy('timeseries.daily_user_activity',
    start_offset => INTERVAL '30 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

-- =============================================
-- SUPABASE INTEGRATION
-- =============================================

-- Supabase auth schema (simplified version)
CREATE TABLE auth.users (
    id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    email VARCHAR(180) NOT NULL UNIQUE,
    encrypted_password TEXT NOT NULL,
    email_confirmed_at TIMESTAMPTZ,
    confirmation_token TEXT,
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token TEXT,
    recovery_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB DEFAULT '{}',
    raw_user_meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE auth.users IS 'Supabase auth users';

-- Supabase storage schema (simplified version)
CREATE TABLE storage.buckets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    owner UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    public BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE storage.buckets IS 'Supabase storage buckets';

CREATE TABLE storage.objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id TEXT NOT NULL REFERENCES storage.buckets(id),
    name TEXT NOT NULL,
    owner UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    path_tokens TEXT[] GENERATED ALWAYS AS (string_to_array(name, '/')) STORED,
    UNIQUE(bucket_id, name)
);

COMMENT ON TABLE storage.objects IS 'Supabase storage objects';

-- Supabase realtime schema (simplified version)
CREATE TABLE realtime.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE realtime.subscriptions IS 'Supabase realtime subscriptions';

-- Row Level Security (RLS) policies
-- Example RLS policy function
CREATE OR REPLACE FUNCTION supabase.check_user_access(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (auth.uid() = user_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- AGENT MODULE (SUPERAGI INTEGRATION)
-- =============================================

-- Agents
CREATE TABLE command_cauldron.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    model VARCHAR(100) NOT NULL,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE command_cauldron.agents IS 'AI agents for autonomous operations';

-- Agent executions
CREATE TABLE command_cauldron.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES command_cauldron.agents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    result JSONB,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE command_cauldron.agent_executions IS 'Execution history of AI agents';

-- Agent tools
CREATE TABLE command_cauldron.agent_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    tool_type VARCHAR(100) NOT NULL,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE command_cauldron.agent_tools IS 'Tools available to AI agents';

-- Agent-tool associations
CREATE TABLE command_cauldron.agent_tool_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES command_cauldron.agents(id) ON DELETE CASCADE,
    tool_id UUID NOT NULL REFERENCES command_cauldron.agent_tools(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_id, tool_id)
);

COMMENT ON TABLE command_cauldron.agent_tool_associations IS 'Tools assigned to agents';

-- Agent workflows
CREATE TABLE command_cauldron.workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE command_cauldron.workflows IS 'Workflows for agent orchestration';

-- Workflow executions
CREATE TABLE command_cauldron.workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES command_cauldron.workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    result JSONB,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE command_cauldron.workflow_executions IS 'Execution history of workflows';

-- =============================================
-- INTEGRATION POINTS
-- =============================================

-- External system connections
CREATE TABLE integration.connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(180) NOT NULL,
    system_type VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE integration.connections IS 'External system connection configurations';

-- Data sync jobs
CREATE TABLE integration.sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES integration.connections(id) ON DELETE CASCADE,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    stats JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE integration.sync_jobs IS 'Data synchronization job history';

-- Event bus
CREATE TABLE integration.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    source VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE integration.events IS 'Event bus for system integration';

-- =============================================
-- INDEXES
-- =============================================

-- Core indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON public.user_sessions(expires_at);
CREATE INDEX idx_api_tokens_user_id ON public.api_tokens(user_id);
CREATE INDEX idx_user_roles_user_id ON public.user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON public.user_roles(role_id);
CREATE INDEX idx_role_permissions_role_id ON public.role_permissions(role_id);
CREATE INDEX idx_permissions_module ON public.permissions(module);
CREATE INDEX idx_teams_organization_id ON public.teams(organization_id);
CREATE INDEX idx_team_members_team_id ON public.team_members(team_id);
CREATE INDEX idx_team_members_user_id ON public.team_members(user_id);
CREATE INDEX idx_organization_users_organization_id ON public.organization_users(organization_id);
CREATE INDEX idx_organization_users_user_id ON public.organization_users(user_id);
CREATE INDEX idx_organization_invitations_email ON public.organization_invitations(email);
CREATE INDEX idx_organization_invitations_expires_at ON public.organization_invitations(expires_at);
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type_id ON public.audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_organization_settings_organization_id ON public.organization_settings(organization_id);
CREATE INDEX idx_user_settings_user_id ON public.user_settings(user_id);

-- Lore module indexes
CREATE INDEX idx_documents_created_at ON lore.documents(created_at);
CREATE INDEX idx_documents_created_by ON lore.documents(created_by);
CREATE INDEX idx_document_chunks_document_id ON lore.document_chunks(document_id);
CREATE INDEX idx_document_category_associations_document_id ON lore.document_category_associations(document_id);
CREATE INDEX idx_document_category_associations_category_id ON lore.document_category_associations(category_id);
CREATE INDEX idx_document_tag_associations_document_id ON lore.document_tag_associations(document_id);
CREATE INDEX idx_document_tag_associations_tag_id ON lore.document_tag_associations(tag_id);
CREATE INDEX idx_document_teams_document_id ON lore.document_teams(document_id);
CREATE INDEX idx_document_teams_team_id ON lore.document_teams(team_id);
CREATE INDEX idx_document_versions_document_id ON lore.document_versions(document_id);
CREATE INDEX idx_entities_entity_type ON lore.entities(entity_type);
CREATE INDEX idx_relationships_source_entity_id ON lore.relationships(source_entity_id);
CREATE INDEX idx_relationships_target_entity_id ON lore.relationships(target_entity_id);
CREATE INDEX idx_relationships_relationship_type ON lore.relationships(relationship_type);
CREATE INDEX idx_entity_document_associations_entity_id ON lore.entity_document_associations(entity_id);
CREATE INDEX idx_entity_document_associations_document_id ON lore.entity_document_associations(document_id);
CREATE INDEX idx_entity_mentions_entity_id ON lore.entity_mentions(entity_id);
CREATE INDEX idx_entity_mentions_document_id ON lore.entity_mentions(document_id);
CREATE INDEX idx_entity_mentions_chunk_id ON lore.entity_mentions(chunk_id);
CREATE INDEX idx_search_queries_user_id ON lore.search_queries(user_id);
CREATE INDEX idx_search_queries_created_at ON lore.search_queries(created_at);
CREATE INDEX idx_search_results_query_id ON lore.search_results(query_id);
CREATE INDEX idx_search_results_chunk_id ON lore.search_results(chunk_id);

-- Vector indexes for similarity search
CREATE INDEX ON lore.document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON lore.entities USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON lore.search_queries USING hnsw (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX idx_documents_fts ON lore.documents USING GIN (to_tsvector('english', title || ' ' || content));
CREATE INDEX idx_entities_fts ON lore.entities USING GIN (to_tsvector('english', name || ' ' || description));

-- TimescaleDB indexes
CREATE INDEX idx_system_metrics_host_metric ON timeseries.system_metrics(host, metric_name, time DESC);
CREATE INDEX idx_user_activity_user_id ON timeseries.user_activity(user_id, time DESC);
CREATE INDEX idx_business_metrics_org_metric ON timeseries.business_metrics(organization_id, metric_name, time DESC);
CREATE INDEX idx_agent_metrics_agent_id ON timeseries.agent_metrics(agent_id, time DESC);

-- Agent module indexes
CREATE INDEX idx_agents_organization_id ON command_cauldron.agents(organization_id);
CREATE INDEX idx_agents_created_by ON command_cauldron.agents(created_by);
CREATE INDEX idx_agent_executions_agent_id ON command_cauldron.agent_executions(agent_id);
CREATE INDEX idx_agent_executions_status ON command_cauldron.agent_executions(status);
CREATE INDEX idx_agent_tool_associations_agent_id ON command_cauldron.agent_tool_associations(agent_id);
CREATE INDEX idx_workflows_organization_id ON command_cauldron.workflows(organization_id);
CREATE INDEX idx_workflow_executions_workflow_id ON command_cauldron.workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON command_cauldron.workflow_executions(status);

-- Integration indexes
CREATE INDEX idx_connections_organization_id ON integration.connections(organization_id);
CREATE INDEX idx_sync_jobs_connection_id ON integration.sync_jobs(connection_id);
CREATE INDEX idx_sync_jobs_status ON integration.sync_jobs(status);
CREATE INDEX idx_events_event_type ON integration.events(event_type);
CREATE INDEX idx_events_status ON integration.events(status);
CREATE INDEX idx_events_created_at ON integration.events(created_at);

-- =============================================
-- FUNCTIONS AND PROCEDURES
-- =============================================

-- Vector similarity search function
CREATE OR REPLACE FUNCTION vector.search_documents(
    query_text TEXT,
    embedding_vector VECTOR(1536),
    limit_results INTEGER DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.7
) RETURNS TABLE (
    document_id UUID,
    chunk_id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS document_id,
        c.id AS chunk_id,
        c.content,
        1 - (c.embedding <=> embedding_vector) AS similarity,
        c.metadata
    FROM
        lore.document_chunks c
    JOIN
        lore.documents d ON c.document_id = d.id
    WHERE
        1 - (c.embedding <=> embedding_vector) > similarity_threshold
        AND d.is_archived = FALSE
    ORDER BY
        c.embedding <=> embedding_vector
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Time-series aggregation function
CREATE OR REPLACE FUNCTION timeseries.aggregate_metrics(
    metric_name TEXT,
    time_bucket_interval INTERVAL,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
) RETURNS TABLE (
    bucket TIMESTAMPTZ,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        time_bucket(time_bucket_interval, time) AS bucket,
        AVG(metric_value) AS avg_value,
        MIN(metric_value) AS min_value,
        MAX(metric_value) AS max_value,
        COUNT(*) AS count
    FROM
        timeseries.system_metrics
    WHERE
        time >= start_time
        AND time <= end_time
        AND metric_name = aggregate_metrics.metric_name
    GROUP BY
        bucket
    ORDER BY
        bucket;
END;
$$ LANGUAGE plpgsql;

-- Audit logging procedure
CREATE OR REPLACE PROCEDURE audit.log_action(
    user_id UUID,
    action VARCHAR(50),
    entity_type VARCHAR(100),
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT
) AS $$
BEGIN
    INSERT INTO public.audit_logs (
        user_id,
        action,
        entity_type,
        entity_id,
        details,
        ip_address,
        user_agent
    ) VALUES (
        user_id,
        action,
        entity_type,
        entity_id,
        details,
        ip_address,
        user_agent
    );
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- TRIGGERS
-- =============================================

-- Update modified_at timestamp
CREATE OR REPLACE FUNCTION public.update_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with modified_at column
CREATE TRIGGER update_users_modified_at
BEFORE UPDATE ON public.users
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_user_profiles_modified_at
BEFORE UPDATE ON public.user_profiles
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_roles_modified_at
BEFORE UPDATE ON public.roles
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_organizations_modified_at
BEFORE UPDATE ON public.organizations
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_teams_modified_at
BEFORE UPDATE ON public.teams
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_system_settings_modified_at
BEFORE UPDATE ON public.system_settings
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_organization_settings_modified_at
BEFORE UPDATE ON public.organization_settings
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_user_settings_modified_at
BEFORE UPDATE ON public.user_settings
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_documents_modified_at
BEFORE UPDATE ON lore.documents
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_document_categories_modified_at
BEFORE UPDATE ON lore.document_categories
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_entities_modified_at
BEFORE UPDATE ON lore.entities
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_relationships_modified_at
BEFORE UPDATE ON lore.relationships
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_entity_types_modified_at
BEFORE UPDATE ON lore.entity_types
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_relationship_types_modified_at
BEFORE UPDATE ON lore.relationship_types
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_agents_modified_at
BEFORE UPDATE ON command_cauldron.agents
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_agent_tools_modified_at
BEFORE UPDATE ON command_cauldron.agent_tools
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_workflows_modified_at
BEFORE UPDATE ON command_cauldron.workflows
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

CREATE TRIGGER update_connections_modified_at
BEFORE UPDATE ON integration.connections
FOR EACH ROW EXECUTE FUNCTION public.update_modified_at();

-- =============================================
-- PARTITIONING STRATEGY
-- =============================================

-- Example of partitioning for audit logs (by time)
CREATE TABLE audit.partitioned_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE audit.logs_y2023m01 PARTITION OF audit.partitioned_logs
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
    
CREATE TABLE audit.logs_y2023m02 PARTITION OF audit.partitioned_logs
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- Function to create new partitions automatically
CREATE OR REPLACE FUNCTION audit.create_partition_and_insert()
RETURNS TRIGGER AS $$
DECLARE
    partition_date TEXT;
    partition_name TEXT;
BEGIN
    partition_date := to_char(NEW.created_at, 'YYYY_MM');
    partition_name := 'audit.logs_' || partition_date;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                  WHERE c.relname = 'logs_' || partition_date AND n.nspname = 'audit') THEN
        EXECUTE format('CREATE TABLE %I PARTITION OF audit.partitioned_logs
                        FOR VALUES FROM (%L) TO (%L)',
                        partition_name,
                        date_trunc('month', NEW.created_at),
                        date_trunc('month', NEW.created_at) + interval '1 month');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_audit_log_trigger
    BEFORE INSERT ON audit.partitioned_logs
    FOR EACH ROW EXECUTE FUNCTION audit.create_partition_and_insert();

-- =============================================
-- BACKUP AND RECOVERY
-- =============================================

-- WAL archiving settings (to be configured in postgresql.conf)
-- wal_level = replica
-- archive_mode = on
-- archive_command = 'cp %p /var/lib/postgresql/archive/%f'
-- archive_timeout = 60

-- Backup procedure
CREATE OR REPLACE PROCEDURE admin.create_backup(
    backup_name TEXT
) AS $$
BEGIN
    EXECUTE format('SELECT pg_start_backup(%L)', backup_name);
    -- External script would copy files here
    EXECUTE 'SELECT pg_stop_backup()';
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- INITIAL DATA
-- =============================================

-- Insert default roles
INSERT INTO public.roles (name, description, is_system_role)
VALUES 
    ('System Administrator', 'Full access to all system functions', TRUE),
    ('User', 'Standard user with basic access', TRUE),
    ('Manager', 'Access to manage teams and view reports', TRUE),
    ('Developer', 'Access to development tools and APIs', TRUE),
    ('Analyst', 'Access to analytics and reporting', TRUE);

-- Insert default permissions
INSERT INTO public.permissions (name, description, module)
VALUES
    ('user.create', 'Create new users', 'core'),
    ('user.read', 'View user information', 'core'),
    ('user.update', 'Update user information', 'core'),
    ('user.delete', 'Delete users', 'core'),
    ('role.manage', 'Manage roles and permissions', 'core'),
    ('settings.manage', 'Manage system settings', 'core'),
    ('api.access', 'Access API endpoints', 'core'),
    ('lore.read', 'Access knowledge base', 'lore'),
    ('lore.write', 'Create and update knowledge', 'lore'),
    ('lore.admin', 'Administer knowledge base', 'lore'),
    ('agent.create', 'Create new agents', 'superagi'),
    ('agent.execute', 'Execute agent workflows', 'superagi'),
    ('agent.manage', 'Manage agent configurations', 'superagi');

-- Insert initial system settings
INSERT INTO public.system_settings (key, value, description, is_system)
VALUES
    ('system.name', '"Cauldron sEOS"', 'System name displayed in UI', TRUE),
    ('system.version', '"1.0.0"', 'Current system version', TRUE),
    ('auth.password_policy', '{"min_length": 8, "require_uppercase": true, "require_number": true, "require_special": true}', 'Password policy settings', TRUE),
    ('auth.session_timeout', '86400', 'Session timeout in seconds (24 hours)', TRUE),
    ('email.enabled', 'true', 'Whether email notifications are enabled', TRUE),
    ('lore.embedding_model', '"text-embedding-ada-002"', 'Default embedding model for knowledge management', TRUE),
    ('lore.embedding_dimensions', '1536', 'Dimensions for vector embeddings', TRUE),
    ('agent.default_model', '"gpt-4"', 'Default LLM for agent operations', TRUE);

-- Insert default entity types
INSERT INTO lore.entity_types (name, description, properties)
VALUES
    ('Person', 'A person or individual', '{"attributes": ["name", "title", "organization", "expertise"]}'),
    ('Organization', 'A company, institution, or group', '{"attributes": ["name", "industry", "location", "size"]}'),
    ('Concept', 'An abstract idea or notion', '{"attributes": ["name", "domain", "definition"]}'),
    ('Technology', 'A technology, tool, or platform', '{"attributes": ["name", "category", "version", "vendor"]}'),
    ('Process', 'A business process or workflow', '{"attributes": ["name", "domain", "steps", "owner"]}'),
    ('Location', 'A physical or virtual location', '{"attributes": ["name", "type", "coordinates"]}');

-- Insert default relationship types
INSERT INTO lore.relationship_types (name, description, source_types, target_types)
VALUES
    ('WORKS_FOR', 'Employment relationship', ARRAY['Person'], ARRAY['Organization']),
    ('KNOWS', 'Knowledge or expertise in a subject', ARRAY['Person'], ARRAY['Concept', 'Technology', 'Process']),
    ('PART_OF', 'Component or membership relationship', ARRAY['Person', 'Organization', 'Concept', 'Process'], ARRAY['Organization', 'Concept', 'Process']),
    ('USES', 'Usage relationship', ARRAY['Person', 'Organization', 'Process'], ARRAY['Technology', 'Process']),
    ('LOCATED_IN', 'Physical or logical location', ARRAY['Person', 'Organization'], ARRAY['Location']),
    ('RELATED_TO', 'General relationship', NULL, NULL);

-- Create default storage buckets
INSERT INTO storage.buckets (id, name, public)
VALUES
    ('documents', 'Document Storage', FALSE),
    ('avatars', 'User Avatars', TRUE),
    ('attachments', 'Message Attachments', FALSE);

-- Record initial migration
INSERT INTO public.schema_migrations (version, description, applied_by)
VALUES ('20230101000000', 'Initial schema creation', 'setup');