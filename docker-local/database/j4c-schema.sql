-- J4C (Jeeves4coders) Database Schema
-- Complete schema for J4C Analytics Dashboard

-- ============================================================================
-- ROLES AND PERMISSIONS
-- ============================================================================

-- Create roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert J4C roles
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'J4C System Administrator', '{
    "user_management": true,
    "system_config": true,
    "all_projects": true,
    "all_metrics": true,
    "export_all": true,
    "ai_insights": true,
    "real_time_alerts": true,
    "jira_admin": true,
    "github_admin": true,
    "audit_logs": true
}'),
('team_lead', 'J4C Team Lead', '{
    "team_metrics": true,
    "project_progress": true,
    "performance_analytics": true,
    "export_team": true,
    "ai_insights": true,
    "real_time_alerts": true,
    "jira_team": true,
    "github_team": true
}'),
('developer', 'J4C Developer', '{
    "personal_metrics": true,
    "assigned_tasks": true,
    "code_quality": true,
    "export_personal": true,
    "ai_insights": true,
    "jira_personal": true,
    "github_personal": true
}'),
('viewer', 'J4C Viewer', '{
    "view_public": true,
    "general_metrics": true,
    "ai_insights": true
}');

-- ============================================================================
-- USERS
-- ============================================================================

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    password_hash VARCHAR(255),
    role_id UUID NOT NULL REFERENCES roles(id),
    avatar_url TEXT,
    google_id VARCHAR(255),
    github_username VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert J4C admin user
INSERT INTO users (email, username, full_name, role_id, is_active, email_verified) 
SELECT 
    'subbu@aurigraph.io',
    'subbu_j4c_admin',
    'Subbu Jois (J4C Admin)',
    r.id,
    true,
    true
FROM roles r WHERE r.name = 'admin';

-- ============================================================================
-- PROJECTS
-- ============================================================================

-- Create projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_key VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    repository_url TEXT,
    jira_project_key VARCHAR(20),
    jira_board_id VARCHAR(20),
    confluence_space_key VARCHAR(20),
    team_lead_id UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert J4C project
INSERT INTO projects (
    project_key, 
    name, 
    description, 
    repository_url, 
    jira_project_key, 
    jira_board_id,
    team_lead_id,
    metadata
) VALUES (
    'J4C',
    'Jeeves4coders (Engineering Automation Agent)',
    'Comprehensive engineering automation and analytics platform for development teams',
    'https://github.com/Instoradmin/Jeeves4coders.git',
    'J4C',
    '327',
    (SELECT id FROM users WHERE email = 'subbu@aurigraph.io'),
    '{
        "github_org": "Instoradmin",
        "github_repo": "Jeeves4coders",
        "tech_stack": ["Python", "TypeScript", "React", "FastAPI", "PostgreSQL"],
        "team_size": 5,
        "project_type": "Engineering Automation",
        "start_date": "2024-01-01",
        "status": "active"
    }'
);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Code metrics table
CREATE TABLE code_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    file_path TEXT,
    commit_hash VARCHAR(40),
    branch_name VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Performance metrics table
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20),
    success BOOLEAN DEFAULT true,
    duration_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Error reports table
CREATE TABLE error_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    file_path TEXT,
    line_number INTEGER,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- JIRA metrics table
CREATE TABLE jira_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    ticket_key VARCHAR(20) NOT NULL,
    ticket_type VARCHAR(50),
    status VARCHAR(50),
    priority VARCHAR(20),
    assignee_id UUID REFERENCES users(id),
    reporter_id UUID REFERENCES users(id),
    story_points INTEGER,
    time_spent_seconds INTEGER,
    created_date TIMESTAMP WITH TIME ZONE,
    resolved_date TIMESTAMP WITH TIME ZONE,
    sprint_name VARCHAR(100),
    epic_key VARCHAR(20),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- GitHub metrics table
CREATE TABLE github_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    metric_type VARCHAR(50) NOT NULL, -- commits, prs, reviews, issues
    metric_value INTEGER NOT NULL,
    repository VARCHAR(100),
    branch VARCHAR(100),
    pr_number INTEGER,
    commit_sha VARCHAR(40),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Usage statistics table
CREATE TABLE usage_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    feature_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- AI insights table
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_active ON users(is_active);

-- Projects indexes
CREATE INDEX idx_projects_key ON projects(project_key);
CREATE INDEX idx_projects_active ON projects(is_active);
CREATE INDEX idx_projects_team_lead ON projects(team_lead_id);

-- Code metrics indexes
CREATE INDEX idx_code_metrics_project_timestamp ON code_metrics(project_id, timestamp DESC);
CREATE INDEX idx_code_metrics_user_timestamp ON code_metrics(user_id, timestamp DESC);
CREATE INDEX idx_code_metrics_type ON code_metrics(metric_type);

-- Performance metrics indexes
CREATE INDEX idx_performance_metrics_project_timestamp ON performance_metrics(project_id, timestamp DESC);
CREATE INDEX idx_performance_metrics_name ON performance_metrics(metric_name);

-- Error reports indexes
CREATE INDEX idx_error_reports_project_status ON error_reports(project_id, status);
CREATE INDEX idx_error_reports_created ON error_reports(created_at DESC);
CREATE INDEX idx_error_reports_assigned ON error_reports(assigned_to);

-- JIRA metrics indexes
CREATE INDEX idx_jira_metrics_project ON jira_metrics(project_id);
CREATE INDEX idx_jira_metrics_ticket ON jira_metrics(ticket_key);
CREATE INDEX idx_jira_metrics_status ON jira_metrics(status);
CREATE INDEX idx_jira_metrics_assignee ON jira_metrics(assignee_id);

-- GitHub metrics indexes
CREATE INDEX idx_github_metrics_project_timestamp ON github_metrics(project_id, timestamp DESC);
CREATE INDEX idx_github_metrics_user_timestamp ON github_metrics(user_id, timestamp DESC);
CREATE INDEX idx_github_metrics_type ON github_metrics(metric_type);

-- Usage statistics indexes
CREATE INDEX idx_usage_statistics_user_timestamp ON usage_statistics(user_id, timestamp DESC);
CREATE INDEX idx_usage_statistics_feature ON usage_statistics(feature_name);

-- AI insights indexes
CREATE INDEX idx_ai_insights_user ON ai_insights(user_id);
CREATE INDEX idx_ai_insights_project ON ai_insights(project_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_expires ON ai_insights(expires_at);

-- Audit logs indexes
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_error_reports_updated_at BEFORE UPDATE ON error_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO j4c_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO j4c_user;

-- Log schema creation
DO $$
BEGIN
    RAISE NOTICE 'J4C Database schema created successfully!';
    RAISE NOTICE 'Tables created: %, %, %, %, %, %, %, %, %, %', 
        'roles', 'users', 'projects', 'code_metrics', 'performance_metrics', 
        'error_reports', 'jira_metrics', 'github_metrics', 'usage_statistics', 'ai_insights';
END $$;
