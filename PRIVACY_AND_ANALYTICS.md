# Jeeves4coders Privacy & Analytics System

## 🛡️ Your Code is Safe - Privacy Guarantee

**Jeeves4coders NEVER accesses, stores, or transmits your source code.** Your intellectual property remains completely secure and private.

### What We Collect
- ✅ Anonymous usage statistics (which features you use)
- ✅ Error logs (sanitized, no code content)
- ✅ Performance metrics (execution times)
- ✅ System information (OS, Python version)
- ✅ User feedback (when you choose to provide it)

### What We DO NOT Collect
- ❌ **Source code content**
- ❌ **File names or directory structures**
- ❌ **Project-specific information**
- ❌ **Proprietary algorithms or business logic**
- ❌ **Database schemas or configurations**
- ❌ **API keys or sensitive credentials**
- ❌ **Personal files or documents**

## 🎯 Purpose of Data Collection

### Bug Detection & Fixing
- Identify software crashes and errors
- Improve tool stability and reliability
- Prioritize bug fixes based on frequency

### Feature Improvement
- Understand which features are most valuable
- Optimize performance based on usage patterns
- Guide development of new capabilities

### User Support
- Provide better technical assistance
- Create helpful documentation and guides
- Improve user experience

## 🔧 Privacy Controls

### Check Your Privacy Status
```bash
jeeves4coders privacy status
```

### Opt Out of All Analytics
```bash
jeeves4coders privacy opt-out
```

### Opt Back In
```bash
jeeves4coders privacy opt-in
```

### Submit Feedback
```bash
# General feedback
jeeves4coders privacy feedback --message "Great tool, love the automation!"

# Bug report
jeeves4coders privacy feedback --feedback-type bug --message "Found an issue with..." --rating 3

# Feature request
jeeves4coders privacy feedback --feedback-type feature_request --message "Would love to see..."
```

## 📊 Analytics Dashboard

### For Users
You can view your privacy status and analytics preferences:
- User ID (anonymous hash)
- Analytics enabled/disabled status
- Last privacy consent date
- Data collection preferences

### For Aurigraph
Aggregated, anonymous analytics help us:
- Track adoption and usage trends
- Identify common error patterns
- Measure feature effectiveness
- Plan product roadmap

## 🔒 Data Security

### Encryption
- All data transmitted using HTTPS/TLS
- Data at rest encrypted in secure databases
- Access controls and authentication required

### Anonymization
- User IDs are cryptographic hashes
- No personally identifiable information stored
- All code content automatically stripped

### Data Retention
- Usage analytics: 2 years maximum
- Error reports: 1 year maximum
- Feedback: Indefinite (for product improvement)
- User accounts: Until deletion requested

## 🌍 Legal Compliance

### GDPR (European Users)
- Right to access your data
- Right to correct inaccurate data
- Right to delete your data
- Right to data portability
- Right to object to processing

### CCPA (California Users)
- Right to know what data is collected
- Right to delete personal information
- Right to opt-out of data sales (we don't sell data)
- Right to non-discrimination

### Contact for Privacy Requests
- Email: privacy@aurigraph.io
- Subject: "Jeeves4coders Privacy Request"
- Include your User ID for faster processing

## 🚀 Getting Started with Analytics

### First Time Setup
1. Install Jeeves4coders
2. Run `jeeves4coders init`
3. Review privacy policy and consent
4. Start using the tool - analytics are automatic

### Customizing Your Experience
1. Check current settings: `jeeves4coders privacy status`
2. Adjust preferences as needed
3. Provide feedback to help us improve

## 🔧 Technical Implementation

### Local Processing
- All code analysis happens on your machine
- No source code leaves your environment
- Only metadata and statistics are collected

### Fail-Safe Design
- Analytics failures never affect tool functionality
- Network issues don't block your work
- All analytics calls have short timeouts

### Data Sanitization
Automatic removal of:
- File paths and directory names
- Code snippets and content
- Sensitive strings (passwords, tokens, keys)
- Personal information
- Project-specific details

## 📈 Analytics Data Flow

```
Your Machine                    Aurigraph Servers
┌─────────────────┐            ┌──────────────────┐
│ Jeeves4coders   │            │ Analytics API    │
│                 │            │                  │
│ ┌─────────────┐ │   HTTPS    │ ┌──────────────┐ │
│ │ Code        │ │ ────────── │ │ Usage Stats  │ │
│ │ Analysis    │ │ Metadata   │ │ Error Logs   │ │
│ │ (Local)     │ │ Only       │ │ Performance  │ │
│ └─────────────┘ │            │ │ Metrics      │ │
│                 │            │ └──────────────┘ │
│ ┌─────────────┐ │            │                  │
│ │ Source Code │ │            │ ┌──────────────┐ │
│ │ NEVER       │ │     ❌     │ │ Source Code  │ │
│ │ TRANSMITTED │ │ ────────── │ │ NEVER        │ │
│ └─────────────┘ │            │ │ STORED       │ │
└─────────────────┘            │ └──────────────┘ │
                               └──────────────────┘
```

## 🛠️ For Developers

### Testing Analytics Locally
1. Start the mock server:
   ```bash
   python mock-analytics-server.py
   ```

2. Set environment variable:
   ```bash
   export JEEVES_ANALYTICS_URL="http://localhost:8080/api/v1"
   ```

3. Run Jeeves4coders normally - analytics will go to local server

### Disabling Analytics in CI/CD
```bash
# Disable analytics for automated environments
jeeves4coders privacy opt-out
```

### Custom Analytics Endpoint
```bash
# Use custom analytics server
export JEEVES_ANALYTICS_URL="https://your-analytics-server.com/api/v1"
```

## 📞 Support & Contact

### General Support
- Email: support@aurigraph.io
- GitHub: https://github.com/Instoradmin/Jeeves4coders

### Privacy Questions
- Email: privacy@aurigraph.io
- Response time: 48 hours maximum

### Bug Reports
- Use built-in feedback: `jeeves4coders privacy feedback --feedback-type bug`
- GitHub Issues: https://github.com/Instoradmin/Jeeves4coders/issues

### Feature Requests
- Use built-in feedback: `jeeves4coders privacy feedback --feedback-type feature_request`
- GitHub Discussions: https://github.com/Instoradmin/Jeeves4coders/discussions

## 🎉 Thank You

By using Jeeves4coders and allowing anonymous analytics, you're helping us build a better tool for the entire developer community. Your privacy is our priority, and your code is always safe.

**Remember: You can opt out at any time with zero impact on functionality.**

---

**Last Updated:** January 9, 2025  
**Privacy Policy Version:** 1.0.0  
**Contact:** privacy@aurigraph.io
