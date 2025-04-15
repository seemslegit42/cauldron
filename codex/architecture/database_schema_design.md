# Cauldron™ Database Schema Design

## Executive Summary

This document outlines the comprehensive database schema design for the Cauldron™ Sentient Enterprise Operating System (sEOS). The design incorporates PostgreSQL as the foundation, potentially integrating Supabase, a Vector Database (e.g., Qdrant/PGvector), and a Time-Series Database to create a flexible, scalable, and specialized data storage solution that supports the diverse needs of the system.

## 1. Database Architecture Principles

### 1.1 Polyglot Persistence

The Cauldron™ database architecture embraces polyglot persistence, using specialized database technologies for different data types and access patterns:

- **Relational Data**: PostgreSQL for structured, transactional data
- **Vector Data**: PGvector or dedicated vector database for embeddings and similarity search
- **Time-Series Data**: TimescaleDB for metrics, events, and temporal analysis
- **BaaS Features**: Supabase for authentication, storage, and realtime capabilities

### 1.2 Schema Design Principles

The schema design follows these core principles:

- **Domain-Driven Design**: Schema organization reflects business domains
- **Progressive Disclosure**: Simple core with extensible complexity
- **Consistent Conventions**: Standardized naming and structure
- **Performance Optimization**: Indexes, partitioning, and query efficiency
- **Data Integrity**: Constraints, validation, and referential integrity
- **Auditability**: Comprehensive tracking of data changes
- **Multi-tenancy**: Secure isolation between tenant data

## 2. PostgreSQL as Foundation

### 2.1 Core Capabilities

PostgreSQL serves as the primary relational database, providing:

- **ACID Compliance**: Ensuring data integrity and consistency
- **Rich Data Types**: Supporting complex data structures
- **Extensibility**: Enabling specialized functionality through extensions
- **Performance**: Optimized for transactional and analytical workloads
- **Security**: Comprehensive access control and encryption capabilities

### 2.2 Extensions

Key PostgreSQL extensions enhance core functionality:

- **pgvector**: Vector operations and similarity search
- **TimescaleDB**: Time-series data management
- **PostGIS**: Geospatial data and operations
- **pg_stat_statements**: Query performance monitoring
- **pg_partman**: Table partitioning management
- **pg_audit**: Comprehensive audit logging
- **pg_cron**: Scheduled database operations

## 3. Schema Organization

### 3.1 Schema Structure

The database is organized into logical schemas:

- **public**: Core Frappe and ERPNext tables
- **core**: Fundamental system entities (users, permissions, etc.)
- **lore**: Knowledge management and RAG capabilities
- **synapse**: Business intelligence and analytics
- **aegis**: Security and compliance
- **command**: DevOps and development
- **aether**: Agent orchestration and management

### 3.2 Common Tables

Each schema includes common table types:

- **Master Data**: Core reference entities
- **Transactional Data**: Business events and operations
- **Configuration Data**: System and module settings
- **Relationship Data**: Mapping between entities
- **Audit Data**: Historical tracking of changes

## 4. Core Schema Design

### 4.1 Public Schema (Frappe/ERPNext)

The public schema contains standard Frappe and ERPNext tables:

- **tabDocType**: Document type definitions
- **tabDocField**: Field definitions for DocTypes
- **tabUser**: User accounts and profiles
- **tabRole**: Role definitions for permissions
- **tabPermission**: Permission rules
- **tabSingles**: Single-record configuration
- **tabCustom Field**: Custom field definitions
- **tabWorkflow**: Workflow definitions
- **tabWorkflow State**: Workflow state definitions
- **tabWorkflow Action**: Workflow action definitions

### 4.2 Core Schema

The core schema contains fundamental system entities:

```sql
-- Users table
CREATE TABLE core.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_system_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Roles table
CREATE TABLE core.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User roles mapping
CREATE TABLE core.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES core.roles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Permissions table
CREATE TABLE core.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES core.roles(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    can_read BOOLEAN DEFAULT FALSE,
    can_write BOOLEAN DEFAULT FALSE,
    can_create BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_export BOOLEAN DEFAULT FALSE,
    can_import BOOLEAN DEFAULT FALSE,
    can_print BOOLEAN DEFAULT FALSE,
    can_email BOOLEAN DEFAULT FALSE,
    can_report BOOLEAN DEFAULT FALSE,
    can_set_user_permissions BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, resource_type, COALESCE(resource_id, '00000000-0000-0000-0000-000000000000'::UUID))
);

-- Organizations table
CREATE TABLE core.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    logo_url TEXT,
    primary_contact_email VARCHAR(255),
    primary_contact_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Teams table
CREATE TABLE core.teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES core.organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- Team members
CREATE TABLE core.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES core.teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    is_team_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Audit log
CREATE TABLE core.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES core.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 5. Vector Database Integration

### 5.1 PGvector Implementation

Vector database capabilities are implemented through the pgvector extension:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Document chunks with embeddings
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

-- Create HNSW index for fast similarity search
CREATE INDEX ON lore.document_chunks USING hnsw (embedding vector_cosine_ops);
```

### 5.2 Dedicated Vector Database Option

For larger deployments, a dedicated vector database like Qdrant may be used:

- **Collections**: Organized by embedding type and domain
- **Vectors**: Stored with associated metadata
- **Indexes**: HNSW or other ANN algorithms
- **Filtering**: Metadata-based filtering during search
- **Versioning**: Support for model evolution

## 6. Time-Series Database Integration

### 6.1 TimescaleDB Implementation

Time-series data is managed through the TimescaleDB extension:

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Metrics table
CREATE TABLE synapse.metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    dimensions JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('synapse.metrics', 'time');

-- Create indexes
CREATE INDEX idx_metrics_metric_name ON synapse.metrics(metric_name);
CREATE INDEX idx_metrics_dimensions ON synapse.metrics USING GIN(dimensions);

-- Create continuous aggregate for hourly rollups
CREATE MATERIALIZED VIEW synapse.metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    metric_name,
    dimensions,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM synapse.metrics
GROUP BY bucket, metric_name, dimensions;

-- Add refresh policy
SELECT add_continuous_aggregate_policy('synapse.metrics_hourly',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Add retention policy
SELECT add_retention_policy('synapse.metrics', INTERVAL '90 days');
```

### 6.2 Specialized Time-Series Tables

Different time-series data types have specialized tables:

- **Metrics**: Numerical measurements over time
- **Events**: Discrete occurrences with timestamps
- **Logs**: Structured logging data
- **Telemetry**: System and application performance data
- **Forecasts**: Predicted future values

## 7. Supabase Integration

### 7.1 Authentication and Authorization

Supabase provides authentication services:

```sql
-- Enable Supabase Auth schema
CREATE SCHEMA IF NOT EXISTS auth;

-- Auth users table (simplified example)
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255) NOT NULL,
    email_confirmed_at TIMESTAMPTZ,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMPTZ,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMPTZ,
    last_sign_in_at TIMESTAMPTZ,
    raw_app_meta_data JSONB DEFAULT '{}',
    raw_user_meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Map Supabase auth users to core users
CREATE TABLE core.auth_user_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id UUID NOT NULL UNIQUE,
    core_user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 7.2 Storage

Supabase storage for file management:

```sql
-- Enable Supabase Storage schema
CREATE SCHEMA IF NOT EXISTS storage;

-- Buckets table
CREATE TABLE storage.buckets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    owner UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    public BOOLEAN DEFAULT FALSE
);

-- Objects table
CREATE TABLE storage.objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id UUID NOT NULL REFERENCES storage.buckets(id),
    name TEXT NOT NULL,
    owner UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    path_tokens TEXT[] GENERATED ALWAYS AS (string_to_array(name, '/')) STORED,
    UNIQUE(bucket_id, name)
);
```

## 8. Module-Specific Schemas

### 8.1 Lore Schema (Knowledge Management)

The Lore schema manages knowledge and RAG capabilities:

```sql
-- Documents table
CREATE TABLE lore.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    source_type VARCHAR(50),
    created_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE
);

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

-- Knowledge sources
CREATE TABLE lore.knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    connection_config JSONB NOT NULL,
    sync_frequency VARCHAR(50) DEFAULT 'daily',
    last_synced_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Skill profiles
CREATE TABLE lore.skill_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    skills JSONB DEFAULT '{}',
    expertise_areas JSONB DEFAULT '{}',
    confidence_scores JSONB DEFAULT '{}',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 8.2 Aegis Schema (Security)

The Aegis schema manages security and compliance:

```sql
-- Security events
CREATE TABLE aegis.security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    raw_data JSONB,
    processed_data JSONB,
    is_incident BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('aegis.security_events', 'event_time');

-- Threats
CREATE TABLE aegis.threats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    threat_name VARCHAR(255) NOT NULL,
    threat_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    description TEXT,
    indicators JSONB DEFAULT '{}',
    mitigations JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerabilities
CREATE TABLE aegis.vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id VARCHAR(50), -- CVE or custom ID
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    cvss_score FLOAT,
    affected_systems JSONB DEFAULT '{}',
    remediation_steps TEXT,
    status VARCHAR(50) DEFAULT 'open',
    discovered_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security playbooks
CREATE TABLE aegis.security_playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_conditions JSONB DEFAULT '{}',
    steps JSONB NOT NULL,
    is_automated BOOLEAN DEFAULT FALSE,
    requires_approval BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security incidents
CREATE TABLE aegis.security_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to UUID REFERENCES core.users(id) ON DELETE SET NULL,
    related_events JSONB DEFAULT '{}',
    related_threats JSONB DEFAULT '{}',
    timeline JSONB DEFAULT '{}',
    resolution TEXT,
    lessons_learned TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
```

### 8.3 Synapse Schema (Business Intelligence)

The Synapse schema manages analytics and intelligence:

```sql
-- Analytics metrics
CREATE TABLE synapse.analytics_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    description TEXT,
    unit_of_measure VARCHAR(50),
    is_percentage BOOLEAN DEFAULT FALSE,
    is_currency BOOLEAN DEFAULT FALSE,
    currency VARCHAR(3),
    calculation_method TEXT,
    data_source VARCHAR(100),
    query_definition TEXT,
    target_value FLOAT,
    warning_threshold FLOAT,
    critical_threshold FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Forecasts
CREATE TABLE synapse.forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_name VARCHAR(255) NOT NULL,
    metric_id UUID NOT NULL REFERENCES synapse.analytics_metrics(id) ON DELETE CASCADE,
    forecast_model VARCHAR(100) NOT NULL,
    forecast_parameters JSONB DEFAULT '{}',
    forecast_date TIMESTAMPTZ NOT NULL,
    forecast_horizon INTEGER NOT NULL,
    forecast_data JSONB NOT NULL,
    performance_metrics JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboards
CREATE TABLE synapse.dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_name VARCHAR(255) NOT NULL,
    description TEXT,
    layout JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_viewed TIMESTAMPTZ
);

-- Dashboard components
CREATE TABLE synapse.dashboard_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID NOT NULL REFERENCES synapse.dashboards(id) ON DELETE CASCADE,
    component_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    metric_id UUID REFERENCES synapse.analytics_metrics(id) ON DELETE SET NULL,
    chart_type VARCHAR(50),
    time_range VARCHAR(20) DEFAULT '30d',
    refresh_frequency VARCHAR(20) DEFAULT '1h',
    size VARCHAR(20) DEFAULT 'medium',
    position JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Business simulations
CREATE TABLE synapse.business_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_name VARCHAR(255) NOT NULL,
    description TEXT,
    model_definition JSONB NOT NULL,
    parameters JSONB DEFAULT '{}',
    scenarios JSONB DEFAULT '{}',
    results JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    created_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_run_at TIMESTAMPTZ
);
```

### 8.4 AetherCore Schema (Agent Orchestration)

The AetherCore schema manages AI agents:

```sql
-- Agent definitions
CREATE TABLE aether.agent_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    description TEXT,
    capabilities JSONB DEFAULT '{}',
    parameters JSONB DEFAULT '{}',
    model_config JSONB DEFAULT '{}',
    tools JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent instances
CREATE TABLE aether.agent_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    definition_id UUID NOT NULL REFERENCES aether.agent_definitions(id) ON DELETE CASCADE,
    instance_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    current_task_id UUID,
    memory JSONB DEFAULT '{}',
    state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ
);

-- Agent tasks
CREATE TABLE aether.agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    assigned_to UUID REFERENCES aether.agent_instances(id) ON DELETE SET NULL,
    created_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Agent interactions
CREATE TABLE aether.agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    agent_instance_id UUID NOT NULL REFERENCES aether.agent_instances(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Human-in-the-loop approvals
CREATE TABLE aether.hitl_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES aether.agent_tasks(id) ON DELETE CASCADE,
    approval_type VARCHAR(50) NOT NULL,
    description TEXT,
    details JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    responded_by UUID REFERENCES core.users(id) ON DELETE SET NULL,
    response JSONB,
    notes TEXT
);
```

## 9. Integration and Migration

### 9.1 Data Integration Strategy

The integration between database components follows these patterns:

- **Foreign Data Wrappers**: Accessing external data sources
- **ETL Pipelines**: Scheduled data transformation and loading
- **Change Data Capture**: Real-time data synchronization
- **API Integration**: Service-based data access
- **Event-Driven Updates**: Reactive data modifications

### 9.2 Migration Strategy

Database schema evolution is managed through:

- **Version-Controlled Migrations**: Tracked schema changes
- **Forward-Only Changes**: No backward-incompatible modifications
- **Blue-Green Deployments**: Minimizing downtime during updates
- **Data Backfilling**: Populating new structures from existing data
- **Compatibility Layers**: Supporting transitional access patterns

## 10. Performance Optimization

### 10.1 Indexing Strategy

Effective indexing improves query performance:

- **Primary Keys**: Unique identification of records
- **Foreign Keys**: Optimizing joins between tables
- **Composite Indexes**: Supporting multi-column conditions
- **Partial Indexes**: Targeting specific data subsets
- **Expression Indexes**: Supporting computed values
- **GIN/GiST Indexes**: For JSONB and full-text search
- **BRIN Indexes**: For large, ordered datasets

### 10.2 Partitioning Strategy

Partitioning improves management of large tables:

- **Time-Based Partitioning**: For historical data
- **Range Partitioning**: For numeric or alphabetical ranges
- **List Partitioning**: For categorical data
- **Hash Partitioning**: For evenly distributed access
- **Partition Pruning**: Optimizing query execution

### 10.3 Query Optimization

Query performance is enhanced through:

- **Prepared Statements**: Reducing parsing overhead
- **Query Planning**: Analyzing execution plans
- **Materialized Views**: Pre-computing complex queries
- **Connection Pooling**: Efficient connection management
- **Caching Layers**: Reducing database load

## 11. Security and Compliance

### 11.1 Data Protection

Data security is implemented through:

- **Row-Level Security**: Fine-grained access control
- **Column-Level Encryption**: Protecting sensitive data
- **Data Masking**: Obscuring confidential information
- **Audit Logging**: Tracking data access and changes
- **Backup and Recovery**: Protecting against data loss

### 11.2 Compliance Features

Regulatory compliance is supported through:

- **Data Retention Policies**: Managing data lifecycle
- **GDPR Compliance**: Supporting right to access/erasure
- **Audit Trails**: Documenting all data modifications
- **Data Lineage**: Tracking data origins and transformations
- **Access Controls**: Enforcing least privilege principle

## 12. Conclusion

The Cauldron™ Database Schema Design provides a comprehensive framework for storing, accessing, and managing the diverse data types required by the Sentient Enterprise Operating System. By leveraging PostgreSQL as the foundation and integrating specialized database technologies for vector, time-series, and BaaS capabilities, the design creates a flexible, scalable, and high-performance data layer that supports the full range of system requirements.

The schema organization reflects the domain-driven design of the system, with clear separation between modules while maintaining consistent patterns and conventions. The integration of advanced features like vector embeddings, time-series analytics, and multi-tenancy support enables the sophisticated AI capabilities that define the Cauldron™ sEOS.

This database schema design serves as the blueprint for implementing the data foundation of the Cauldron™ system, guiding development efforts and ensuring alignment with the overall architectural vision.