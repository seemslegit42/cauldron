-- Create schemas for Cauldron sEOS

-- Default schema for shared tables
-- public schema already exists by default

-- ERPNext core tables
CREATE SCHEMA IF NOT EXISTS erp;
COMMENT ON SCHEMA erp IS 'ERPNext core tables';

-- HR module tables
CREATE SCHEMA IF NOT EXISTS hr;
COMMENT ON SCHEMA hr IS 'HR module tables';

-- CRM module tables
CREATE SCHEMA IF NOT EXISTS crm;
COMMENT ON SCHEMA crm IS 'CRM module tables';

-- Command & Cauldron module tables
CREATE SCHEMA IF NOT EXISTS command_cauldron;
COMMENT ON SCHEMA command_cauldron IS 'Command & Cauldron module tables for AI Software Development & Autonomous DevOps';

-- Synapse module tables
CREATE SCHEMA IF NOT EXISTS synapse;
COMMENT ON SCHEMA synapse IS 'Synapse module tables for Predictive & Prescriptive Business Intelligence';

-- Aegis Protocol module tables
CREATE SCHEMA IF NOT EXISTS aegis;
COMMENT ON SCHEMA aegis IS 'Aegis Protocol module tables for Proactive & Autonomous Cybersecurity';

-- Lore module tables
CREATE SCHEMA IF NOT EXISTS lore;
COMMENT ON SCHEMA lore IS 'Lore module tables for Collective Intelligence & Knowledge Synthesis';

-- Vector embeddings (PGVector)
CREATE SCHEMA IF NOT EXISTS vector;
COMMENT ON SCHEMA vector IS 'Vector embeddings using PGVector';

-- Time-series data (TimescaleDB)
CREATE SCHEMA IF NOT EXISTS timeseries;
COMMENT ON SCHEMA timeseries IS 'Time-series data using TimescaleDB';

-- Audit and logging tables
CREATE SCHEMA IF NOT EXISTS audit;
COMMENT ON SCHEMA audit IS 'Audit and logging tables';

-- Admin functions and procedures
CREATE SCHEMA IF NOT EXISTS admin;
COMMENT ON SCHEMA admin IS 'Administrative functions and procedures';
