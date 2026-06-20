# Security Policy and Compliance Guide

## Security Overview

CloudSync employs enterprise-grade security measures to protect your data at every layer of our infrastructure. This document outlines our security practices, compliance certifications, and what you can do to maximize your account security.

## Data Encryption

### Encryption at Rest
- All data encrypted using AES-256
- Encryption keys managed by AWS KMS (Key Management Service)
- Customer-managed keys (CMK) available for Enterprise plans
- Database backups encrypted with separate key set

### Encryption in Transit
- TLS 1.2 minimum, TLS 1.3 preferred
- HSTS (HTTP Strict Transport Security) enabled
- Certificate Transparency logging
- Perfect Forward Secrecy (PFS) enabled

### End-to-End Encryption (Enterprise)
- Optional E2E encryption for sensitive workspace data
- Keys generated client-side, never transmitted to servers
- Enables zero-knowledge architecture for sensitive fields

## Access Controls

### Role-Based Access Control (RBAC)
**Default Roles:**
- **Owner**: Full access, billing management, workspace deletion
- **Admin**: Manage users, settings, and integrations
- **Editor**: Create and modify records, upload files
- **Viewer**: Read-only access to specified data
- **Guest**: Limited access to shared items only

**Custom Roles (Business and Enterprise):**
Create roles with granular permissions:
- Record-level permissions
- Field-level visibility controls
- IP-restricted access roles

### Single Sign-On (SSO)
**Supported Protocols:**
- SAML 2.0
- OpenID Connect (OIDC)
- OAuth 2.0

**Supported Identity Providers:**
- Okta
- Azure Active Directory
- Google Workspace
- OneLogin
- Custom SAML providers

**Setting Up SSO:**
1. Settings → Security → Single Sign-On
2. Select your identity provider
3. Upload metadata XML or enter manual configuration
4. Map user attributes (email, name, department)
5. Test with a pilot user before enabling for all

### IP Allowlisting
Restrict access to specific IP ranges:
1. Settings → Security → IP Restrictions
2. Add IP addresses or CIDR ranges
3. Apply to entire workspace or specific roles
4. Emergency bypass via mobile 2FA

## Audit Logging

### What's Logged
- All user authentication events (login, logout, failed attempts)
- Data access and modifications
- Permission changes
- Settings modifications
- API key usage
- File uploads and downloads

### Accessing Audit Logs
- Dashboard → Security → Audit Logs
- Filter by user, action type, date range, resource
- Export to CSV or SIEM tools
- Log retention: 90 days (Pro), 1 year (Business), 7 years (Enterprise)

### SIEM Integration
Export logs to:
- Splunk
- Datadog
- AWS CloudWatch
- Azure Sentinel
- Custom webhook destination

## Compliance Certifications

### Current Certifications
- **SOC 2 Type II**: Annual audit, covers Security, Availability, and Confidentiality
- **ISO 27001**: Information Security Management System
- **GDPR**: Full compliance for EU data subjects
- **HIPAA**: Business Associate Agreements available for healthcare customers
- **PCI DSS Level 2**: For payment data handling

### Requesting Compliance Documents
Enterprise customers can request:
- SOC 2 report (requires NDA)
- Penetration test results summary
- Vendor security assessment questionnaire
- Data processing agreements (DPA)

Contact: security@cloudsync.io

## Data Residency

### Available Regions
- **US East** (Virginia, USA) — Default
- **US West** (Oregon, USA)
- **EU West** (Ireland, EU)
- **EU Central** (Frankfurt, EU)
- **APAC** (Singapore)
- **APAC** (Sydney, Australia)

### Choosing Your Region
Region is set at workspace creation and cannot be changed after data is stored.
For migration between regions, contact enterprise support.

### Data Sovereignty
Enterprise customers can configure:
- Data never leaves specified geographic boundary
- Backup replication within same region only
- Processing restricted to approved regions

## Vulnerability Management

### Bug Bounty Program
CloudSync runs a responsible disclosure program.
Report vulnerabilities to: security@cloudsync.io
Rewards: $100 - $10,000 depending on severity

### Security Updates
- Critical patches applied within 4 hours
- High severity within 24 hours
- Medium severity within 7 days
- Security changelog at status.cloudsync.io/security

## Incident Response

### Security Breach Notification
CloudSync will notify affected customers:
- Within 72 hours of confirmed breach (GDPR requirement)
- Via email to workspace owner and security contact
- Via status page posting
- With details of what was affected, steps taken, and recommendations

### What to Do if You Suspect Compromise
1. Immediately revoke all API keys at Settings → API Keys
2. Force all users to reset passwords: Settings → Security → Force Password Reset
3. Review audit logs for suspicious activity
4. Contact security@cloudsync.io
5. Enable additional 2FA requirement for all users

## User Security Recommendations

### For Individual Users
- Use a unique, strong password
- Enable 2FA (authenticator app preferred over SMS)
- Review active sessions at Settings → Security → Active Sessions
- Log out from unused devices

### For Administrators
- Enforce 2FA for all workspace members
- Enable IP allowlisting for admin accounts
- Review user access quarterly
- Disable inactive accounts promptly
- Set session timeout to 8 hours or less
