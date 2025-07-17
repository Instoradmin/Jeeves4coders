-- J4C (Jeeves4coders) Database Initialization
-- Creates the database and basic configuration for J4C Analytics Dashboard

-- Create database if it doesn't exist (this runs automatically via POSTGRES_DB)
-- CREATE DATABASE j4c_analytics;

-- Connect to the database
\c j4c_analytics;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'team_lead', 'developer', 'viewer');
CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'resolved', 'closed', 'cancelled');
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE metric_type AS ENUM ('quality_score', 'coverage', 'complexity', 'debt', 'performance', 'error_rate');

-- Create J4C specific configuration table
CREATE TABLE j4c_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert J4C specific configuration
INSERT INTO j4c_config (config_key, config_value, description) VALUES
('project_name', 'Jeeves4coders', 'J4C Project Name'),
('project_key', 'J4C', 'JIRA Project Key'),
('jira_board_id', '327', 'JIRA Board ID for J4C'),
('jira_base_url', 'https://instor.atlassian.net', 'JIRA Base URL'),
('github_org', 'Instoradmin', 'GitHub Organization'),
('github_repo', 'Jeeves4coders', 'GitHub Repository'),
('admin_email', 'subbu@aurigraph.io', 'Primary Admin Email'),
('company_name', 'Aurigraph', 'Company Name'),
('support_email', 'support@aurigraph.io', 'Support Email'),
('dashboard_version', '1.0.0', 'Dashboard Version'),
('environment', 'development', 'Current Environment'),
('enable_ai_insights', 'true', 'Enable AI Insights Feature'),
('enable_real_time', 'true', 'Enable Real-time Updates'),
('enable_jira_sync', 'true', 'Enable JIRA Synchronization'),
('enable_github_sync', 'true', 'Enable GitHub Synchronization'),
('cache_ttl_seconds', '300', 'Default Cache TTL in Seconds'),
('analytics_retention_days', '365', 'Analytics Data Retention Period'),
('audit_retention_days', '2555', 'Audit Log Retention Period (7 years)'),
('max_export_records', '10000', 'Maximum Records for Export'),
('websocket_heartbeat_interval', '30', 'WebSocket Heartbeat Interval'),
('ai_insights_cache_ttl', '1800', 'AI Insights Cache TTL'),
('jira_sync_interval', '300', 'JIRA Sync Interval in Seconds');

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for j4c_config
CREATE TRIGGER update_j4c_config_updated_at 
    BEFORE UPDATE ON j4c_config 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to get J4C configuration
CREATE OR REPLACE FUNCTION get_j4c_config(key_name TEXT)
RETURNS TEXT AS $$
DECLARE
    config_val TEXT;
BEGIN
    SELECT config_value INTO config_val 
    FROM j4c_config 
    WHERE config_key = key_name AND is_active = true;
    
    RETURN config_val;
END;
$$ LANGUAGE plpgsql;

-- Create function to set J4C configuration
CREATE OR REPLACE FUNCTION set_j4c_config(key_name TEXT, key_value TEXT, key_description TEXT DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO j4c_config (config_key, config_value, description)
    VALUES (key_name, key_value, key_description)
    ON CONFLICT (config_key) 
    DO UPDATE SET 
        config_value = EXCLUDED.config_value,
        description = COALESCE(EXCLUDED.description, j4c_config.description),
        updated_at = NOW();
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Create J4C specific indexes for performance
CREATE INDEX IF NOT EXISTS idx_j4c_config_key ON j4c_config(config_key);
CREATE INDEX IF NOT EXISTS idx_j4c_config_active ON j4c_config(is_active);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO j4c_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO j4c_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO j4c_user;

-- Create database info view
CREATE OR REPLACE VIEW j4c_database_info AS
SELECT 
    'J4C Analytics Database' as database_name,
    current_database() as database,
    current_user as user,
    version() as postgresql_version,
    NOW() as initialized_at,
    (SELECT config_value FROM j4c_config WHERE config_key = 'dashboard_version') as dashboard_version,
    (SELECT config_value FROM j4c_config WHERE config_key = 'environment') as environment;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'J4C Database initialized successfully!';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE 'Timestamp: %', NOW();
END $$;
