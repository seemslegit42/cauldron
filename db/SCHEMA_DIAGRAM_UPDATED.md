# Cauldron sEOS Database Schema Diagram

This document provides a visual representation of the Cauldron sEOS database schema using Mermaid diagrams.

## Core Schema Relationships

```mermaid
erDiagram
    USERS ||--o{ USER_PROFILES : has
    USERS ||--o{ USER_ROLES : has
    USERS ||--o{ USER_SESSIONS : has
    USERS ||--o{ API_TOKENS : has
    USERS ||--o{ USER_SETTINGS : has
    USERS ||--o{ ORGANIZATION_USERS : belongs_to
    USERS ||--o{ TEAM_MEMBERS : belongs_to
    
    ROLES ||--o{ USER_ROLES : assigned_to
    ROLES ||--o{ ROLE_PERMISSIONS : has
    
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : assigned_to
    
    ORGANIZATIONS ||--o{ TEAMS : has
    ORGANIZATIONS ||--o{ ORGANIZATION_USERS : has
    ORGANIZATIONS ||--o{ ORGANIZATION_SETTINGS : has
    ORGANIZATIONS ||--o{ ORGANIZATION_INVITATIONS : has
    
    TEAMS ||--o{ TEAM_MEMBERS : has
    
    AUDIT_LOGS }o--|| USERS : performed_by
    
    SYSTEM_SETTINGS ||--o{ ORGANIZATION_SETTINGS : overrides
    SYSTEM_SETTINGS ||--o{ USER_SETTINGS : overrides
```

## Lore Module (Vector Database)

```mermaid
erDiagram
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : chunked_into
    DOCUMENTS ||--o{ DOCUMENT_CATEGORY_ASSOCIATIONS : categorized_by
    DOCUMENTS ||--o{ DOCUMENT_TAG_ASSOCIATIONS : tagged_with
    DOCUMENTS ||--o{ DOCUMENT_TEAMS : accessible_by
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : versioned_as
    DOCUMENTS ||--o{ ENTITY_DOCUMENT_ASSOCIATIONS : referenced_by
    DOCUMENTS ||--o{ ENTITY_MENTIONS : contains
    
    DOCUMENT_CATEGORIES ||--o{ DOCUMENT_CATEGORY_ASSOCIATIONS : assigned_to
    DOCUMENT_CATEGORIES ||--o{ DOCUMENT_CATEGORIES : parent_of
    
    DOCUMENT_TAGS ||--o{ DOCUMENT_TAG_ASSOCIATIONS : assigned_to
    
    TEAMS ||--o{ DOCUMENT_TEAMS : has_access_to
    
    DOCUMENT_CHUNKS ||--o{ ENTITY_MENTIONS : contains
    DOCUMENT_CHUNKS ||--o{ SEARCH_RESULTS : matched_in
    
    ENTITIES ||--o{ ENTITY_DOCUMENT_ASSOCIATIONS : mentioned_in
    ENTITIES ||--o{ ENTITY_MENTIONS : referenced_as
    ENTITIES ||--o{ RELATIONSHIPS : source_of
    ENTITIES ||--o{ RELATIONSHIPS : target_of
    
    ENTITY_TYPES ||--o{ ENTITIES : typed_as
    
    RELATIONSHIP_TYPES ||--o{ RELATIONSHIPS : typed_as
```

## Vector Module (Generic Embeddings)

```mermaid
erDiagram
    EMBEDDINGS {
        uuid id
        text content
        vector embedding
        jsonb metadata
        varchar entity_type
        uuid entity_id
        varchar model
        int dimensions
        timestamptz created_at
    }
    
    EMBEDDING_MODELS {
        uuid id
        varchar name
        varchar provider
        int dimensions
        varchar version
        text description
        jsonb configuration
        boolean is_default
    }
    
    COLLECTIONS {
        uuid id
        varchar name
        text description
        uuid model_id
        jsonb metadata_schema
        uuid organization_id
    }
    
    COLLECTION_ITEMS {
        uuid id
        uuid collection_id
        uuid embedding_id
    }
    
    SEARCH_QUERIES {
        uuid id
        text query_text
        vector query_embedding
        uuid model_id
        uuid user_id
        jsonb filters
        int top_k
        float similarity_threshold
    }
    
    SEARCH_RESULTS {
        uuid id
        uuid query_id
        uuid embedding_id
        float similarity_score
        int rank
    }
    
    EMBEDDING_MODELS ||--o{ EMBEDDINGS : generated_by
    EMBEDDING_MODELS ||--o{ COLLECTIONS : used_by
    EMBEDDING_MODELS ||--o{ SEARCH_QUERIES : used_by
    
    EMBEDDINGS ||--o{ COLLECTION_ITEMS : included_in
    EMBEDDINGS ||--o{ SEARCH_RESULTS : matched_in
    
    COLLECTIONS ||--o{ COLLECTION_ITEMS : contains
    
    SEARCH_QUERIES ||--o{ SEARCH_RESULTS : produced
    USERS ||--o{ SEARCH_QUERIES : performed_by
```

## TimeSeries Module

```mermaid
erDiagram
    SYSTEM_METRICS {
        timestamptz time
        varchar host
        varchar metric_name
        double metric_value
        jsonb tags
    }
    
    USER_ACTIVITY {
        timestamptz time
        uuid user_id
        varchar activity_type
        jsonb details
        varchar ip_address
        text user_agent
    }
    
    BUSINESS_METRICS {
        timestamptz time
        uuid organization_id
        varchar metric_name
        double metric_value
        jsonb dimensions
    }
    
    AGENT_METRICS {
        timestamptz time
        uuid agent_id
        uuid execution_id
        varchar metric_name
        double metric_value
        jsonb tags
    }
    
    EVENTS {
        timestamptz time
        varchar event_type
        varchar source
        uuid user_id
        uuid organization_id
        varchar entity_type
        uuid entity_id
        varchar severity
        jsonb details
    }
    
    ALERTS {
        timestamptz time
        varchar alert_type
        varchar source
        varchar severity
        varchar status
        text title
        text description
        uuid assigned_to
    }
    
    ANOMALIES {
        timestamptz time
        varchar metric_name
        varchar entity_type
        uuid entity_id
        double expected_value
        double actual_value
        double deviation_percent
        varchar severity
    }
    
    FORECAST_MODELS {
        uuid id
        varchar name
        text description
        varchar target_metric
        varchar model_type
        jsonb parameters
        jsonb accuracy_metrics
    }
    
    FORECASTS {
        timestamptz time
        uuid model_id
        varchar metric_name
        varchar entity_type
        uuid entity_id
        double forecast_value
        double confidence_lower
        double confidence_upper
    }
    
    USERS ||--o{ USER_ACTIVITY : performed_by
    ORGANIZATIONS ||--o{ BUSINESS_METRICS : measured_for
    FORECAST_MODELS ||--o{ FORECASTS : generated
    USERS ||--o{ ALERTS : assigned_to
```

## Supabase Integration

```mermaid
erDiagram
    AUTH_USERS {
        uuid id
        varchar email
        varchar phone
        varchar encrypted_password
        timestamptz email_confirmed_at
        jsonb raw_app_meta_data
        jsonb raw_user_meta_data
        boolean is_super_admin
    }
    
    AUTH_SESSIONS {
        uuid id
        uuid user_id
        timestamptz created_at
        varchar aal
        timestamptz not_after
    }
    
    AUTH_IDENTITIES {
        uuid id
        uuid user_id
        jsonb identity_data
        varchar provider
    }
    
    USER_MAPPINGS {
        uuid id
        uuid auth_user_id
        uuid app_user_id
    }
    
    STORAGE_BUCKETS {
        text id
        text name
        uuid owner
        boolean public
        bigint file_size_limit
        text[] allowed_mime_types
    }
    
    STORAGE_OBJECTS {
        uuid id
        text bucket_id
        text name
        uuid owner
        jsonb metadata
        text[] path_tokens
    }
    
    FILE_METADATA {
        uuid id
        uuid object_id
        text title
        text description
        text[] tags
        varchar entity_type
        uuid entity_id
        uuid organization_id
    }
    
    ACCESS_CONTROLS {
        uuid id
        uuid object_id
        text bucket_id
        varchar entity_type
        uuid entity_id
        varchar permission
    }
    
    AUTH_USERS ||--o{ AUTH_SESSIONS : has
    AUTH_USERS ||--o{ AUTH_IDENTITIES : has
    AUTH_USERS ||--|| USER_MAPPINGS : mapped_to
    USERS ||--|| USER_MAPPINGS : mapped_to
    
    STORAGE_BUCKETS ||--o{ STORAGE_OBJECTS : contains
    STORAGE_OBJECTS ||--o{ FILE_METADATA : described_by
    STORAGE_OBJECTS ||--o{ ACCESS_CONTROLS : controlled_by
    STORAGE_BUCKETS ||--o{ ACCESS_CONTROLS : controlled_by
```

## Physical Storage Organization

```mermaid
graph TD
    subgraph PostgreSQL
        subgraph Extensions
            PGVector["PGVector (vector)"]
            TimescaleDB["TimescaleDB"]
            PostGIS["PostGIS (geospatial)"]
            pgRouting["pgRouting (graph)"]
            UUID["uuid-ossp"]
            Crypto["pgcrypto"]
            FTS["pg_trgm (full-text search)"]
        end
        
        subgraph Schemas
            Public["public (core)"]
            Lore["lore (knowledge)"]
            TimeSeries["timeseries (metrics)"]
            Vector["vector (embeddings)"]
            CommandCauldron["command_cauldron (agents)"]
            Synapse["synapse (BI)"]
            Aegis["aegis (security)"]
            Integration["integration"]
            Supabase["supabase, auth, storage, realtime"]
            Audit["audit"]
            Admin["admin"]
        end
        
        subgraph Optimizations
            Indexes["Indexes"]
            VectorIndexes["HNSW Vector Indexes"]
            Partitioning["Time-based Partitioning"]
            ContinuousAggregates["Continuous Aggregates"]
            RLS["Row-Level Security"]
        end
    end
    
    Extensions --> Schemas
    Schemas --> Optimizations
```

## Data Flow

```mermaid
flowchart TD
    subgraph External
        Client["Client Applications"]
        API["API Layer"]
        ETL["ETL Processes"]
        AI["AI Services"]
    end
    
    subgraph Database
        subgraph Core["Core Data"]
            Users["Users & Auth"]
            Orgs["Organizations"]
            RBAC["Roles & Permissions"]
        end
        
        subgraph Knowledge["Knowledge Management"]
            Docs["Documents"]
            Vectors["Vector Embeddings"]
            KG["Knowledge Graph"]
        end
        
        subgraph TS["Time Series"]
            Metrics["Metrics"]
            Events["Events"]
            Forecasts["Forecasts"]
        end
        
        subgraph Storage["Storage"]
            Files["Files"]
            Metadata["File Metadata"]
        end
    end
    
    Client <--> API
    API <--> Users
    API <--> Orgs
    API <--> RBAC
    API <--> Docs
    API <--> Vectors
    API <--> KG
    API <--> Metrics
    API <--> Events
    API <--> Forecasts
    API <--> Files
    API <--> Metadata
    
    ETL --> Docs
    ETL --> Metrics
    
    AI <--> Vectors
    AI <--> KG
    AI --> Forecasts
    
    Docs --> Vectors
    Metrics --> Forecasts
    Files --> Metadata
```

This diagram provides a visual representation of the Cauldron sEOS database schema, showing the relationships between tables and the overall architecture. You can render these diagrams using Mermaid-compatible tools or viewers.