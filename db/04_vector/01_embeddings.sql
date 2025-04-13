-- Vector database module - Generic embeddings and similarity search

-- Create schema for vector operations (if not already created)
CREATE SCHEMA IF NOT EXISTS vector;
COMMENT ON SCHEMA vector IS 'Vector embeddings using PGVector';

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

COMMENT ON TABLE vector.embeddings IS 'Generic vector embeddings for various entities';

-- Create HNSW index for fast similarity search
CREATE INDEX ON vector.embeddings USING hnsw (embedding vector_cosine_ops);

-- Create indexes for efficient querying
CREATE INDEX idx_embeddings_entity ON vector.embeddings (entity_type, entity_id);
CREATE INDEX idx_embeddings_model ON vector.embeddings (model);
CREATE INDEX idx_embeddings_metadata ON vector.embeddings USING GIN (metadata);
CREATE INDEX idx_embeddings_created_at ON vector.embeddings (created_at);

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

COMMENT ON TABLE vector.embedding_models IS 'Available embedding models';

-- Insert default embedding models
INSERT INTO vector.embedding_models (name, provider, dimensions, version, description, is_default)
VALUES
    ('text-embedding-ada-002', 'OpenAI', 1536, '002', 'OpenAI Ada embedding model', TRUE),
    ('text-embedding-3-small', 'OpenAI', 1536, '3-small', 'OpenAI small embedding model', FALSE),
    ('text-embedding-3-large', 'OpenAI', 3072, '3-large', 'OpenAI large embedding model', FALSE),
    ('all-MiniLM-L6-v2', 'HuggingFace', 384, 'v2', 'Sentence Transformers MiniLM model', FALSE),
    ('all-mpnet-base-v2', 'HuggingFace', 768, 'v2', 'Sentence Transformers MPNet model', FALSE);

-- Embedding collections table
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

COMMENT ON TABLE vector.collections IS 'Collections of related embeddings';

-- Collection items table
CREATE TABLE vector.collection_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL REFERENCES vector.collections(id) ON DELETE CASCADE,
    embedding_id UUID NOT NULL REFERENCES vector.embeddings(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(collection_id, embedding_id)
);

COMMENT ON TABLE vector.collection_items IS 'Items in embedding collections';

-- Create indexes for collection items
CREATE INDEX idx_collection_items_collection_id ON vector.collection_items (collection_id);
CREATE INDEX idx_collection_items_embedding_id ON vector.collection_items (embedding_id);

-- Search queries log
CREATE TABLE vector.search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_embedding VECTOR(1536),
    model_id UUID REFERENCES vector.embedding_models(id),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    filters JSONB DEFAULT '{}',
    top_k INTEGER DEFAULT 10,
    similarity_threshold FLOAT,
    hybrid_search BOOLEAN DEFAULT FALSE,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE vector.search_queries IS 'Log of vector similarity search queries';

-- Search results log
CREATE TABLE vector.search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES vector.search_queries(id) ON DELETE CASCADE,
    embedding_id UUID NOT NULL REFERENCES vector.embeddings(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    rank INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(query_id, embedding_id)
);

COMMENT ON TABLE vector.search_results IS 'Results of vector similarity searches';

-- Create indexes for search results
CREATE INDEX idx_search_results_query_id ON vector.search_results (query_id);
CREATE INDEX idx_search_results_embedding_id ON vector.search_results (embedding_id);
CREATE INDEX idx_search_results_similarity_score ON vector.search_results (similarity_score);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION vector.similarity_search(
    p_query TEXT,
    p_model_id UUID DEFAULT NULL,
    p_collection_id UUID DEFAULT NULL,
    p_entity_type VARCHAR DEFAULT NULL,
    p_filters JSONB DEFAULT '{}',
    p_top_k INTEGER DEFAULT 10,
    p_similarity_threshold FLOAT DEFAULT 0.7,
    p_hybrid_search BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    entity_type VARCHAR,
    entity_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_query_embedding VECTOR(1536);
    v_model_name VARCHAR;
    v_dimensions INTEGER;
    v_query_id UUID;
    v_start_time TIMESTAMPTZ;
    v_execution_time INTEGER;
    v_user_id UUID;
BEGIN
    v_start_time := clock_timestamp();
    
    -- Get current user ID
    SELECT id INTO v_user_id
    FROM public.users
    WHERE username = current_user;
    
    -- Determine which model to use
    IF p_model_id IS NULL THEN
        SELECT id, name, dimensions INTO p_model_id, v_model_name, v_dimensions
        FROM vector.embedding_models
        WHERE is_default = TRUE
        LIMIT 1;
    ELSE
        SELECT name, dimensions INTO v_model_name, v_dimensions
        FROM vector.embedding_models
        WHERE id = p_model_id;
    END IF;
    
    -- In a real implementation, this would call an external API to get embeddings
    -- For this example, we'll simulate it with a placeholder
    -- v_query_embedding := call_embedding_api(p_query, v_model_name);
    
    -- Placeholder: Generate a random embedding for demonstration
    -- In production, this would be replaced with actual embedding generation
    v_query_embedding := (SELECT ARRAY(
        SELECT random() * 2 - 1
        FROM generate_series(1, v_dimensions)
    )::VECTOR(1536));
    
    -- Log the search query
    INSERT INTO vector.search_queries (
        query_text,
        query_embedding,
        model_id,
        user_id,
        filters,
        top_k,
        similarity_threshold,
        hybrid_search,
        created_at
    ) VALUES (
        p_query,
        v_query_embedding,
        p_model_id,
        v_user_id,
        p_filters,
        p_top_k,
        p_similarity_threshold,
        p_hybrid_search,
        NOW()
    ) RETURNING id INTO v_query_id;
    
    -- Perform the search
    RETURN QUERY
    WITH search_results AS (
        SELECT
            e.id,
            e.content,
            1 - (e.embedding <=> v_query_embedding) AS similarity,
            e.metadata,
            e.entity_type,
            e.entity_id,
            ROW_NUMBER() OVER (ORDER BY 1 - (e.embedding <=> v_query_embedding) DESC) AS rank
        FROM vector.embeddings e
        LEFT JOIN vector.collection_items ci ON e.id = ci.embedding_id
        WHERE (p_collection_id IS NULL OR ci.collection_id = p_collection_id)
          AND (p_entity_type IS NULL OR e.entity_type = p_entity_type)
          AND (1 - (e.embedding <=> v_query_embedding)) >= p_similarity_threshold
          -- Add additional filtering based on p_filters
          -- This would be expanded in a real implementation
        LIMIT p_top_k
    )
    SELECT
        sr.id,
        sr.content,
        sr.similarity,
        sr.metadata,
        sr.entity_type,
        sr.entity_id
    FROM search_results sr
    ORDER BY sr.similarity DESC;
    
    -- Log the results
    INSERT INTO vector.search_results (
        query_id,
        embedding_id,
        similarity_score,
        rank
    )
    SELECT
        v_query_id,
        id,
        similarity,
        ROW_NUMBER() OVER (ORDER BY similarity DESC)
    FROM search_results;
    
    -- Calculate execution time
    v_execution_time := EXTRACT(MILLISECONDS FROM clock_timestamp() - v_start_time)::INTEGER;
    
    -- Update the query with execution time
    UPDATE vector.search_queries
    SET execution_time_ms = v_execution_time
    WHERE id = v_query_id;
END;
$$;

COMMENT ON FUNCTION vector.similarity_search IS 'Perform vector similarity search';

-- Create function to add an embedding
CREATE OR REPLACE FUNCTION vector.add_embedding(
    p_content TEXT,
    p_entity_type VARCHAR,
    p_entity_id UUID,
    p_model_id UUID DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}',
    p_collection_id UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_embedding VECTOR(1536);
    v_model_name VARCHAR;
    v_dimensions INTEGER;
    v_embedding_id UUID;
BEGIN
    -- Determine which model to use
    IF p_model_id IS NULL THEN
        SELECT id, name, dimensions INTO p_model_id, v_model_name, v_dimensions
        FROM vector.embedding_models
        WHERE is_default = TRUE
        LIMIT 1;
    ELSE
        SELECT name, dimensions INTO v_model_name, v_dimensions
        FROM vector.embedding_models
        WHERE id = p_model_id;
    END IF;
    
    -- In a real implementation, this would call an external API to get embeddings
    -- For this example, we'll simulate it with a placeholder
    -- v_embedding := call_embedding_api(p_content, v_model_name);
    
    -- Placeholder: Generate a random embedding for demonstration
    -- In production, this would be replaced with actual embedding generation
    v_embedding := (SELECT ARRAY(
        SELECT random() * 2 - 1
        FROM generate_series(1, v_dimensions)
    )::VECTOR(1536));
    
    -- Insert the embedding
    INSERT INTO vector.embeddings (
        content,
        embedding,
        metadata,
        entity_type,
        entity_id,
        model,
        dimensions
    ) VALUES (
        p_content,
        v_embedding,
        p_metadata,
        p_entity_type,
        p_entity_id,
        v_model_name,
        v_dimensions
    ) RETURNING id INTO v_embedding_id;
    
    -- Add to collection if specified
    IF p_collection_id IS NOT NULL THEN
        INSERT INTO vector.collection_items (
            collection_id,
            embedding_id
        ) VALUES (
            p_collection_id,
            v_embedding_id
        );
    END IF;
    
    RETURN v_embedding_id;
END;
$$;

COMMENT ON FUNCTION vector.add_embedding IS 'Add a new vector embedding';