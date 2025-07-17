# J4C Analytics Dashboard - Docker Local Deployment

## 🚀 **Complete Local Development Environment**

This Docker setup provides a complete local development environment for the J4C (Jeeves4coders) Engineering Automation Agent Analytics Dashboard.

## 📋 **What's Included**

### **🐳 Services**
- **PostgreSQL Database** - J4C analytics data storage
- **Redis Cache** - Session and analytics caching
- **FastAPI Backend** - Analytics API and AI services
- **React Frontend** - Interactive dashboard interface
- **Nginx Proxy** - Reverse proxy and load balancing
- **Adminer** - Database management interface
- **Redis Commander** - Redis management interface

### **🎯 Features**
- ✅ **Complete J4C project integration** with JIRA board 327
- ✅ **Role-based authentication** (Admin, Team Lead, Developer, Viewer)
- ✅ **AI-powered insights** using Google Gemini Pro
- ✅ **Real-time dashboard updates** via WebSockets
- ✅ **JIRA synchronization** for project tracking
- ✅ **GitHub integration** for code metrics
- ✅ **Export capabilities** (PDF, Excel, CSV)
- ✅ **Comprehensive analytics** for engineering metrics

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Required
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 2GB+ disk space

# Optional (for full features)
- Google AI API Key (for AI insights)
- Google OAuth2 credentials
- GitHub OAuth2 credentials
- JIRA API token
```

### **2. Clone and Deploy**
```bash
# Navigate to docker directory
cd docker-local

# Make deployment script executable
chmod +x deploy-j4c.sh

# Deploy J4C Analytics Dashboard
./deploy-j4c.sh
```

### **3. Access the Dashboard**
```bash
# Main Dashboard (via Nginx)
http://localhost:8080

# Direct Frontend Access
http://localhost:3001

# Backend API
http://localhost:8001

# API Documentation
http://localhost:8001/docs
```

## 🔧 **Configuration**

### **Environment Variables**
The deployment script creates `.env.j4c` with these key variables:

```bash
# Google Services (Optional)
J4C_GOOGLE_CLIENT_ID=your-google-client-id
J4C_GOOGLE_AI_API_KEY=your-google-ai-key

# GitHub Integration (Optional)
J4C_GITHUB_CLIENT_ID=your-github-client-id
J4C_GITHUB_TOKEN=your-github-token

# JIRA Integration (Pre-configured)
J4C_JIRA_API_TOKEN=ATATT3xFfGF02M-uwYL27Q-lc-OdO8bb5WSSEFk8QPFOMo_tTdWQZ_qjDX6HhFMYdd2Nh8CN7e1adhBZbg3ERZMq_IJV8KP3fEW5u8G2K4dxGaLevRfNUnVprTFSJGYY03ex2Rr3X_H2yb5ax-0JYGGOfbjiPXJ5tT9EtfgpdhbgFq45k9HgL9g=D139BE86
```

### **Service Ports**
| Service | Port | Description |
|---------|------|-------------|
| Nginx Proxy | 8080 | Main dashboard access |
| Frontend | 3001 | React dashboard |
| Backend API | 8001 | FastAPI backend |
| Database | 5433 | PostgreSQL |
| Redis | 6380 | Redis cache |
| Adminer | 8082 | Database admin |
| Redis Commander | 8083 | Redis admin |

## 👤 **User Management**

### **Default Admin User**
- **Email**: `subbu@aurigraph.io`
- **Role**: Admin (full system access)
- **Setup**: Automatically created on first login

### **User Roles**
1. **Admin** - Full system access, user management
2. **Team Lead** - Team metrics, project management
3. **Developer** - Personal metrics, assigned tasks
4. **Viewer** - Read-only access to public metrics

### **Authentication Methods**
- ✅ **Email/Password** registration
- ✅ **Google OAuth2** (if configured)
- ✅ **GitHub OAuth2** (if configured)

## 📊 **J4C Project Integration**

### **JIRA Integration**
- **Project**: J4C (Jeeves4coders)
- **Board**: https://instor.atlassian.net/jira/software/projects/J4C/boards/327
- **Sync**: Automatic ticket synchronization
- **Metrics**: Sprint velocity, story points, completion rates

### **GitHub Integration**
- **Repository**: Instoradmin/Jeeves4coders
- **Metrics**: Commits, PRs, reviews, issues
- **Code Quality**: Automated analysis and reporting

### **Sample Data**
The deployment includes sample data for development:
- 5 sample users with different roles
- 30 days of code quality metrics
- Performance and error tracking data
- JIRA tickets and GitHub activity
- AI-generated insights

## 🛠️ **Management Commands**

### **Basic Operations**
```bash
# View service status
./deploy-j4c.sh status

# View logs (all services)
./deploy-j4c.sh logs

# Restart services
./deploy-j4c.sh restart

# Stop services
./deploy-j4c.sh stop

# Clean up (removes all data)
./deploy-j4c.sh clean
```

### **Docker Compose Commands**
```bash
# View running containers
docker-compose -f docker-compose.j4c.yml ps

# View logs for specific service
docker-compose -f docker-compose.j4c.yml logs j4c-backend

# Execute commands in containers
docker exec -it j4c-database psql -U j4c_user -d j4c_analytics
docker exec -it j4c-backend python -c "print('Backend is running')"

# Scale services (if needed)
docker-compose -f docker-compose.j4c.yml up -d --scale j4c-backend=2
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :8080
   
   # Stop conflicting services
   sudo systemctl stop apache2  # or nginx
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker logs j4c-database
   
   # Test database connection
   docker exec j4c-database pg_isready -U j4c_user -d j4c_analytics
   ```

3. **Backend API Errors**
   ```bash
   # Check backend logs
   docker logs j4c-backend
   
   # Test API health
   curl http://localhost:8001/health
   ```

4. **Frontend Build Issues**
   ```bash
   # Rebuild frontend
   docker-compose -f docker-compose.j4c.yml build j4c-frontend --no-cache
   ```

### **Health Checks**
```bash
# Database
curl http://localhost:8082  # Adminer

# Backend API
curl http://localhost:8001/health

# Frontend
curl http://localhost:3001/health

# Nginx Proxy
curl http://localhost:8080/health
```

## 📈 **Development Workflow**

### **Code Changes**
1. **Backend Changes**: Mount volume in docker-compose for live reload
2. **Frontend Changes**: Use development mode with hot reload
3. **Database Changes**: Use migrations or update init scripts

### **Testing**
```bash
# Run backend tests
docker exec j4c-backend python -m pytest

# Check code quality
docker exec j4c-backend python -m flake8

# Database tests
docker exec j4c-database psql -U j4c_user -d j4c_analytics -c "SELECT COUNT(*) FROM users;"
```

## 🔐 **Security Notes**

### **Development Security**
- Default passwords are for development only
- Self-signed SSL certificates included
- CORS configured for local development
- Rate limiting enabled on API endpoints

### **Production Considerations**
- Change all default passwords
- Use proper SSL certificates
- Configure proper CORS origins
- Set up proper backup strategies
- Enable audit logging

## 📚 **Additional Resources**

### **Documentation**
- **API Docs**: http://localhost:8001/docs
- **Database Schema**: `database/j4c-schema.sql`
- **Sample Data**: `database/j4c-seed.sql`

### **Monitoring**
- **Database**: Adminer at http://localhost:8082
- **Redis**: Redis Commander at http://localhost:8083
- **Logs**: `docker-compose logs -f`

### **Backup & Restore**
```bash
# Backup database
docker exec j4c-database pg_dump -U j4c_user j4c_analytics > backup.sql

# Restore database
docker exec -i j4c-database psql -U j4c_user j4c_analytics < backup.sql
```

## 🎯 **Next Steps**

1. **Configure API Keys**: Update `.env.j4c` with your actual API keys
2. **Test Authentication**: Try Google/GitHub OAuth login
3. **Explore Dashboard**: Navigate through different role-based views
4. **Generate Insights**: Test AI-powered analytics features
5. **Integrate Data**: Connect your actual JIRA and GitHub data

## 🆘 **Support**

For issues and questions:
- Check the troubleshooting section above
- Review Docker logs: `./deploy-j4c.sh logs`
- Verify service health: `./deploy-j4c.sh status`
- Clean and redeploy: `./deploy-j4c.sh clean && ./deploy-j4c.sh`

---

**🎉 Your J4C Analytics Dashboard is now ready for development!** 🚀
