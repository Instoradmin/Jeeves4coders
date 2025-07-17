-- J4C (Jeeves4coders) Database Seed Data
-- Sample data for development and testing

-- ============================================================================
-- SAMPLE USERS
-- ============================================================================

-- Insert sample developers
INSERT INTO users (email, username, full_name, role_id, is_active, email_verified) VALUES
('developer1@aurigraph.io', 'dev1_j4c', 'John Developer', (SELECT id FROM roles WHERE name = 'developer'), true, true),
('developer2@aurigraph.io', 'dev2_j4c', 'Jane Coder', (SELECT id FROM roles WHERE name = 'developer'), true, true),
('teamlead@aurigraph.io', 'lead_j4c', 'Mike Team Lead', (SELECT id FROM roles WHERE name = 'team_lead'), true, true),
('viewer@aurigraph.io', 'viewer_j4c', 'Sarah Viewer', (SELECT id FROM roles WHERE name = 'viewer'), true, true);

-- ============================================================================
-- SAMPLE CODE METRICS
-- ============================================================================

-- Insert sample code quality metrics for the last 30 days
INSERT INTO code_metrics (project_id, user_id, metric_type, metric_value, file_path, timestamp, metadata) 
SELECT 
    p.id,
    u.id,
    metric_types.type,
    (RANDOM() * 100)::DECIMAL(10,2),
    'src/components/' || metric_types.type || '_component.py',
    NOW() - (RANDOM() * INTERVAL '30 days'),
    '{"language": "python", "framework": "fastapi"}'::JSONB
FROM projects p
CROSS JOIN users u
CROSS JOIN (
    VALUES 
        ('quality_score'),
        ('coverage'),
        ('complexity'),
        ('debt')
) AS metric_types(type)
WHERE p.project_key = 'J4C' 
AND u.email != 'viewer@aurigraph.io'
AND RANDOM() < 0.7; -- 70% chance for each combination

-- ============================================================================
-- SAMPLE PERFORMANCE METRICS
-- ============================================================================

-- Insert sample performance metrics
INSERT INTO performance_metrics (project_id, user_id, metric_name, metric_value, unit, success, duration_ms, timestamp, metadata)
SELECT 
    p.id,
    u.id,
    perf_metrics.name,
    perf_metrics.value + (RANDOM() * 20 - 10)::DECIMAL(10,2), -- Add some variance
    perf_metrics.unit,
    CASE WHEN RANDOM() > 0.1 THEN true ELSE false END, -- 90% success rate
    (RANDOM() * 5000)::INTEGER,
    NOW() - (RANDOM() * INTERVAL '30 days'),
    '{"environment": "development", "version": "1.0.0"}'::JSONB
FROM projects p
CROSS JOIN users u
CROSS JOIN (
    VALUES 
        ('build_time', 120, 'seconds'),
        ('test_execution_time', 45, 'seconds'),
        ('deployment_time', 300, 'seconds'),
        ('api_response_time', 250, 'milliseconds'),
        ('database_query_time', 50, 'milliseconds')
) AS perf_metrics(name, value, unit)
WHERE p.project_key = 'J4C' 
AND u.email != 'viewer@aurigraph.io'
AND RANDOM() < 0.8; -- 80% chance for each combination

-- ============================================================================
-- SAMPLE ERROR REPORTS
-- ============================================================================

-- Insert sample error reports
INSERT INTO error_reports (project_id, user_id, error_type, error_message, file_path, line_number, status, priority, created_at, metadata)
SELECT 
    p.id,
    u.id,
    error_data.type,
    error_data.message,
    error_data.file_path,
    (RANDOM() * 500 + 1)::INTEGER,
    error_data.status,
    error_data.priority,
    NOW() - (RANDOM() * INTERVAL '60 days'),
    '{"browser": "Chrome", "os": "Linux", "version": "1.0.0"}'::JSONB
FROM projects p
CROSS JOIN users u
CROSS JOIN (
    VALUES 
        ('TypeError', 'Cannot read property of undefined', 'src/components/Dashboard.tsx', 'open', 'medium'),
        ('ValidationError', 'Invalid email format', 'src/utils/validation.py', 'resolved', 'low'),
        ('DatabaseError', 'Connection timeout', 'src/database/connection.py', 'open', 'high'),
        ('AuthenticationError', 'Invalid JWT token', 'src/auth/middleware.py', 'resolved', 'medium'),
        ('NetworkError', 'Failed to fetch data', 'src/services/api.ts', 'open', 'low'),
        ('PermissionError', 'Access denied to resource', 'src/auth/permissions.py', 'resolved', 'high')
) AS error_data(type, message, file_path, status, priority)
WHERE p.project_key = 'J4C' 
AND u.email != 'viewer@aurigraph.io'
AND RANDOM() < 0.6; -- 60% chance for each combination

-- ============================================================================
-- SAMPLE JIRA METRICS
-- ============================================================================

-- Insert sample JIRA tickets
INSERT INTO jira_metrics (project_id, ticket_key, ticket_type, status, priority, assignee_id, story_points, time_spent_seconds, created_date, sprint_name, metadata)
SELECT 
    p.id,
    'J4C-' || (ROW_NUMBER() OVER ())::TEXT,
    jira_data.ticket_type,
    jira_data.status,
    jira_data.priority,
    u.id,
    jira_data.story_points,
    jira_data.time_spent_seconds,
    NOW() - (RANDOM() * INTERVAL '90 days'),
    'Sprint ' || (RANDOM() * 10 + 1)::INTEGER,
    ('{"summary": "' || jira_data.summary || '", "components": ["Backend", "Frontend"]}')::JSONB
FROM projects p
CROSS JOIN users u
CROSS JOIN (
    VALUES 
        ('Epic', 'To Do', 'high', 'Implement Analytics Dashboard', 0, 0),
        ('Story', 'In Progress', 'medium', 'Create User Authentication', 8, 28800),
        ('Story', 'Done', 'medium', 'Setup Database Schema', 5, 18000),
        ('Task', 'Done', 'low', 'Write Unit Tests', 3, 10800),
        ('Bug', 'In Progress', 'high', 'Fix Login Issue', 2, 7200),
        ('Story', 'To Do', 'medium', 'Implement AI Insights', 13, 0),
        ('Task', 'Done', 'low', 'Update Documentation', 1, 3600),
        ('Story', 'In Progress', 'high', 'JIRA Integration', 8, 14400),
        ('Bug', 'Done', 'medium', 'Dashboard Loading Issue', 3, 5400),
        ('Task', 'To Do', 'low', 'Code Review', 2, 0)
) AS jira_data(ticket_type, status, priority, summary, story_points, time_spent_seconds)
WHERE p.project_key = 'J4C' 
AND u.email != 'viewer@aurigraph.io'
AND RANDOM() < 0.8; -- 80% chance for each combination

-- ============================================================================
-- SAMPLE GITHUB METRICS
-- ============================================================================

-- Insert sample GitHub metrics
INSERT INTO github_metrics (project_id, user_id, metric_type, metric_value, repository, branch, timestamp, metadata)
SELECT 
    p.id,
    u.id,
    github_data.metric_type,
    (RANDOM() * github_data.max_value + 1)::INTEGER,
    'Jeeves4coders',
    github_data.branch,
    NOW() - (RANDOM() * INTERVAL '30 days'),
    ('{"language": "' || github_data.language || '", "size": ' || (RANDOM() * 1000)::INTEGER || '}')::JSONB
FROM projects p
CROSS JOIN users u
CROSS JOIN (
    VALUES 
        ('commits', 50, 'main', 'Python'),
        ('commits', 30, 'develop', 'Python'),
        ('prs', 10, 'main', 'TypeScript'),
        ('reviews', 15, 'main', 'Python'),
        ('issues', 5, 'main', 'General'),
        ('commits', 20, 'feature/dashboard', 'TypeScript'),
        ('prs', 3, 'develop', 'Python'),
        ('reviews', 8, 'develop', 'TypeScript')
) AS github_data(metric_type, max_value, branch, language)
WHERE p.project_key = 'J4C' 
AND u.email != 'viewer@aurigraph.io'
AND RANDOM() < 0.7; -- 70% chance for each combination

-- ============================================================================
-- SAMPLE USAGE STATISTICS
-- ============================================================================

-- Insert sample usage statistics
INSERT INTO usage_statistics (user_id, project_id, feature_name, action, session_id, timestamp, metadata)
SELECT 
    u.id,
    p.id,
    usage_data.feature_name,
    usage_data.action,
    'session_' || (RANDOM() * 10000)::INTEGER,
    NOW() - (RANDOM() * INTERVAL '7 days'),
    ('{"duration": ' || (RANDOM() * 300)::INTEGER || ', "page": "' || usage_data.page || '"}')::JSONB
FROM users u
CROSS JOIN projects p
CROSS JOIN (
    VALUES 
        ('dashboard', 'view', 'dashboard'),
        ('analytics', 'export', 'analytics'),
        ('user_management', 'create', 'admin'),
        ('code_quality', 'view', 'metrics'),
        ('ai_insights', 'generate', 'insights'),
        ('jira_sync', 'trigger', 'integrations'),
        ('github_sync', 'trigger', 'integrations'),
        ('reports', 'download', 'reports'),
        ('settings', 'update', 'settings'),
        ('profile', 'edit', 'profile')
) AS usage_data(feature_name, action, page)
WHERE p.project_key = 'J4C' 
AND RANDOM() < 0.5; -- 50% chance for each combination

-- ============================================================================
-- SAMPLE AI INSIGHTS
-- ============================================================================

-- Insert sample AI insights
INSERT INTO ai_insights (user_id, project_id, insight_type, title, content, confidence_score, expires_at, metadata)
SELECT 
    u.id,
    p.id,
    ai_data.insight_type,
    ai_data.title,
    ai_data.content,
    (0.7 + RANDOM() * 0.3)::DECIMAL(3,2), -- Confidence between 0.7 and 1.0
    NOW() + INTERVAL '7 days',
    ('{"generated_by": "gemini-pro", "version": "1.0", "tokens": ' || (RANDOM() * 1000 + 100)::INTEGER || '}')::JSONB
FROM users u
CROSS JOIN projects p
CROSS JOIN (
    VALUES 
        ('code_quality', 'Code Quality Improvement Needed', 'Your code quality score has decreased by 5% this week. Consider focusing on test coverage and reducing complexity in the authentication module.'),
        ('performance', 'Build Time Optimization Opportunity', 'Build times have increased by 15% over the last month. Consider optimizing your CI/CD pipeline and reducing dependency installation time.'),
        ('error_analysis', 'Recurring Error Pattern Detected', 'TypeError related to undefined properties has occurred 8 times this week. This suggests a need for better null checking in the frontend components.'),
        ('productivity', 'Team Velocity Trending Up', 'Your team velocity has improved by 20% this sprint. The implementation of automated testing seems to be paying off.'),
        ('technical_debt', 'Technical Debt Alert', 'Technical debt has increased in the database layer. Consider refactoring the connection pooling logic to improve maintainability.')
) AS ai_data(insight_type, title, content)
WHERE p.project_key = 'J4C' 
AND u.email IN ('subbu@aurigraph.io', 'teamlead@aurigraph.io', 'developer1@aurigraph.io')
AND RANDOM() < 0.8; -- 80% chance for each combination

-- ============================================================================
-- SAMPLE AUDIT LOGS
-- ============================================================================

-- Insert sample audit logs
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, new_values, timestamp)
SELECT 
    u.id,
    audit_data.action,
    audit_data.resource_type,
    audit_data.resource_id,
    audit_data.new_values::JSONB,
    NOW() - (RANDOM() * INTERVAL '30 days')
FROM users u
CROSS JOIN (
    VALUES 
        ('user_login', 'user', 'login_session', '{"ip": "192.168.1.100", "user_agent": "Chrome/91.0"}'),
        ('project_created', 'project', 'J4C', '{"name": "Jeeves4coders", "status": "active"}'),
        ('role_assigned', 'user', 'role_assignment', '{"role": "developer", "assigned_by": "admin"}'),
        ('config_updated', 'system', 'configuration', '{"key": "ai_insights", "value": "enabled"}'),
        ('export_generated', 'analytics', 'export', '{"format": "pdf", "records": 1500}'),
        ('insight_generated', 'ai', 'insight', '{"type": "code_quality", "confidence": 0.85}')
) AS audit_data(action, resource_type, resource_id, new_values)
WHERE RANDOM() < 0.6; -- 60% chance for each combination

-- ============================================================================
-- UPDATE STATISTICS
-- ============================================================================

-- Update table statistics for better query planning
ANALYZE;

-- Log seed data completion
DO $$
DECLARE
    user_count INTEGER;
    metric_count INTEGER;
    jira_count INTEGER;
    insight_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO metric_count FROM code_metrics;
    SELECT COUNT(*) INTO jira_count FROM jira_metrics;
    SELECT COUNT(*) INTO insight_count FROM ai_insights;
    
    RAISE NOTICE 'J4C Database seeded successfully!';
    RAISE NOTICE 'Users: %, Code Metrics: %, JIRA Tickets: %, AI Insights: %', 
        user_count, metric_count, jira_count, insight_count;
    RAISE NOTICE 'Sample data ready for development and testing';
END $$;
