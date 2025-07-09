# Aurigraph Analytics API Specification

This document outlines the API endpoints for the Aurigraph user database and analytics system for Jeeves4coders.

## Base URL
```
https://analytics.aurigraph.io/api/v1
```

## Authentication
- No authentication required for basic analytics
- All data is anonymized and privacy-compliant
- No source code content is ever transmitted

## Endpoints

### 1. User Registration
**POST** `/users/register`

Register a new user in the analytics database.

**Request Body:**
```json
{
  "user_id": "string (16-char hash)",
  "registration_date": "ISO 8601 timestamp",
  "system_info": {
    "platform": "Windows/Linux/macOS",
    "platform_version": "string",
    "architecture": "x64/arm64/etc",
    "python_version": "3.x.x",
    "jeeves_version": "1.0.0"
  },
  "privacy_consent": {
    "privacy_policy_version": "1.0.0",
    "consent_date": "ISO 8601 timestamp",
    "analytics_enabled": true,
    "code_safety_acknowledged": true
  }
}
```

**Response:**
- `201 Created`: User registered successfully
- `409 Conflict`: User already exists
- `400 Bad Request`: Invalid data

### 2. Usage Tracking
**POST** `/usage/track`

Track usage events for analytics and improvement.

**Request Body:**
```json
{
  "user_id": "string",
  "session_id": "string (UUID)",
  "event_type": "string (e.g., 'workflow_executed', 'tool_started')",
  "timestamp": "ISO 8601 timestamp",
  "event_data": {
    "module_name": "string (optional)",
    "execution_time": "number (optional)",
    "success": "boolean (optional)"
  },
  "system_context": {
    "platform": "string",
    "jeeves_version": "string",
    "session_duration": "number"
  }
}
```

**Response:**
- `200 OK`: Event tracked successfully
- `400 Bad Request`: Invalid event data

### 3. Error Reporting
**POST** `/errors/report`

Report errors for bug tracking and improvement.

**Request Body:**
```json
{
  "user_id": "string",
  "session_id": "string",
  "error_type": "string (e.g., 'ModuleExecutionError')",
  "error_message": "string (sanitized)",
  "stack_trace": "string (sanitized, optional)",
  "timestamp": "ISO 8601 timestamp",
  "context": {
    "module_name": "string (optional)",
    "execution_time": "number (optional)"
  },
  "system_info": {
    "platform": "string",
    "python_version": "string",
    "jeeves_version": "string"
  }
}
```

**Response:**
- `201 Created`: Error reported successfully
- `400 Bad Request`: Invalid error data

### 4. Feedback Submission
**POST** `/feedback/submit`

Submit user feedback for product improvement.

**Request Body:**
```json
{
  "user_id": "string",
  "feedback_type": "bug|feature_request|general",
  "message": "string",
  "rating": "number (1-5, optional)",
  "timestamp": "ISO 8601 timestamp",
  "metadata": {
    "additional_context": "any"
  },
  "system_info": {
    "platform": "string",
    "jeeves_version": "string"
  }
}
```

**Response:**
- `201 Created`: Feedback submitted successfully
- `400 Bad Request`: Invalid feedback data

### 5. Heartbeat
**POST** `/users/heartbeat`

Send periodic heartbeat to track active users.

**Request Body:**
```json
{
  "user_id": "string",
  "session_id": "string",
  "timestamp": "ISO 8601 timestamp",
  "session_duration": "number",
  "jeeves_version": "string"
}
```

**Response:**
- `200 OK`: Heartbeat received
- `400 Bad Request`: Invalid heartbeat data

## Privacy Guarantees

### What We Collect
- Anonymous usage statistics
- Error logs (sanitized)
- System information
- User feedback
- Performance metrics

### What We DO NOT Collect
- Source code content
- File names or paths
- Project-specific information
- Personal data beyond email (for auth)
- Proprietary algorithms or business logic
- Database schemas or configurations
- API keys or credentials

### Data Sanitization
All data is automatically sanitized to remove:
- File paths and directory structures
- Code snippets or content
- Sensitive strings (passwords, tokens, keys)
- Personal information
- Project-specific details

### User Rights
- Opt-out of all analytics at any time
- Request data deletion
- View collected data
- Modify privacy preferences

## Implementation Notes

### Mock Server for Development
For development and testing, a mock server can be implemented that:
- Returns appropriate HTTP status codes
- Logs requests for debugging
- Validates request schemas
- Simulates network delays

### Error Handling
- All analytics calls should fail silently
- Network failures should not affect tool functionality
- Timeouts should be short (5-10 seconds)
- Retry logic should be minimal to avoid blocking

### Rate Limiting
- Implement client-side rate limiting
- Batch events when possible
- Use exponential backoff for failures

## Database Schema (Reference)

### Users Table
```sql
CREATE TABLE users (
    user_id VARCHAR(16) PRIMARY KEY,
    registration_date TIMESTAMP,
    last_seen TIMESTAMP,
    platform VARCHAR(50),
    platform_version VARCHAR(100),
    architecture VARCHAR(20),
    python_version VARCHAR(20),
    jeeves_version VARCHAR(20),
    privacy_consent_version VARCHAR(10),
    analytics_enabled BOOLEAN DEFAULT TRUE
);
```

### Usage Events Table
```sql
CREATE TABLE usage_events (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(16) REFERENCES users(user_id),
    session_id UUID,
    event_type VARCHAR(100),
    timestamp TIMESTAMP,
    event_data JSONB,
    system_context JSONB
);
```

### Error Reports Table
```sql
CREATE TABLE error_reports (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(16) REFERENCES users(user_id),
    session_id UUID,
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    timestamp TIMESTAMP,
    context JSONB,
    system_info JSONB,
    resolved BOOLEAN DEFAULT FALSE
);
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(16) REFERENCES users(user_id),
    feedback_type VARCHAR(50),
    message TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP,
    metadata JSONB,
    system_info JSONB,
    status VARCHAR(20) DEFAULT 'new'
);
```

## Security Considerations

1. **Data Encryption**: All data in transit and at rest should be encrypted
2. **Access Control**: Limit access to analytics data to authorized personnel only
3. **Data Retention**: Implement automatic data cleanup policies
4. **Anonymization**: Ensure all data is properly anonymized
5. **Audit Logging**: Log all access to analytics data
6. **GDPR Compliance**: Implement data subject rights (access, deletion, portability)

## Monitoring and Alerting

- Monitor API response times and error rates
- Alert on unusual error patterns
- Track user adoption and engagement metrics
- Monitor data quality and completeness
- Set up dashboards for key metrics

---

**Contact Information:**
- API Support: api-support@aurigraph.io
- Privacy Questions: privacy@aurigraph.io
- Technical Issues: tech-support@aurigraph.io
