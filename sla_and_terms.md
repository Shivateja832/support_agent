# Service Level Agreement (SLA) and Terms of Service

## Service Level Commitments

### Uptime Guarantees by Plan

| Plan | Uptime SLA | Max Monthly Downtime |
|------|-----------|---------------------|
| Free | No SLA | N/A |
| Pro | 99.9% | 43.8 minutes |
| Business | 99.95% | 21.9 minutes |
| Enterprise | 99.99% | 4.4 minutes |

### Measuring Uptime
Uptime is measured on a monthly basis, calculated as:
`(Total Minutes - Downtime Minutes) / Total Minutes × 100`

Excluded from downtime calculation:
- Scheduled maintenance (announced 48 hours in advance)
- Force majeure events (natural disasters, internet backbone failures)
- Customer-caused outages (misconfigured webhooks, API abuse)
- Third-party service outages (AWS, Cloudflare)

### Scheduled Maintenance
- Frequency: Monthly, maximum 4 hours
- Timing: Tuesday 2:00 AM - 6:00 AM UTC
- Notification: Email and status page 48 hours prior
- Emergency maintenance may occur with shorter notice

## Service Credits

### Credit Calculation
When uptime falls below SLA:

| Uptime Achieved | Credit (% of Monthly Fee) |
|----------------|--------------------------|
| 99.0% - 99.9% | 10% |
| 95.0% - 99.0% | 25% |
| Below 95.0% | 50% |

### Claiming Credits
1. Credits must be requested within 30 days of incident
2. Submit at billing@cloudsync.io with subject "SLA Credit Request"
3. Include: Incident dates, your monitoring data (optional)
4. Processing: 5-10 business days
5. Applied to next invoice (not refunded to payment method)

## Support Response Times

### Ticket Priority Levels

**P1 - Critical (System Down)**
- Definition: Complete service unavailability affecting all users
- Pro: 2-hour initial response, 4-hour resolution target
- Business: 1-hour initial response, 2-hour resolution target
- Enterprise: 15-minute initial response, 1-hour resolution target

**P2 - High (Major Feature Impaired)**
- Definition: Core functionality unavailable for significant portion of users
- Pro: 4-hour initial response
- Business: 2-hour initial response
- Enterprise: 1-hour initial response

**P3 - Medium (Minor Feature Issue)**
- Definition: Non-critical feature unavailable, workaround available
- Pro: 8-hour initial response
- Business: 4-hour initial response
- Enterprise: 2-hour initial response

**P4 - Low (General Question/Enhancement)**
- Definition: How-to questions, feature requests, cosmetic issues
- All plans: 1 business day response

### Support Channels by Plan

| Channel | Free | Pro | Business | Enterprise |
|---------|------|-----|----------|------------|
| Documentation | ✓ | ✓ | ✓ | ✓ |
| Community Forum | ✓ | ✓ | ✓ | ✓ |
| Email Support | ✗ | ✓ | ✓ | ✓ |
| Live Chat | ✗ | ✓ | ✓ | ✓ |
| Phone Support | ✗ | ✗ | ✓ | ✓ |
| Dedicated CSM | ✗ | ✗ | ✗ | ✓ |
| 24/7 Support | ✗ | ✗ | ✗ | ✓ |

## Data Retention and Deletion

### Data Retention Policy
- Active account data: Retained indefinitely while subscribed
- Deleted records: Soft-deleted, recoverable for 30 days
- After 30 days: Permanently purged from all systems
- Audit logs: See audit log retention by plan

### Account Deletion
When an account is deleted:
- Day 0: Account deleted, data queued for purge
- Day 30: All data permanently deleted from primary storage
- Day 45: Purged from backups
- Day 60: Purged from all disaster recovery systems

### Data Export Before Deletion
Export your data before closing your account:
Settings → Data → Export All Data
Formats available: CSV, JSON, XML
Download link valid for 7 days after export

## Acceptable Use Policy

### Prohibited Uses
- Storing illegal content
- Using the service to conduct unauthorized access to other systems
- Sending spam or bulk unsolicited communications
- Mining cryptocurrency using CloudSync infrastructure
- Overloading systems beyond reasonable use (abuse of API)
- Reverse engineering the service
- Reselling access without authorization

### Fair Use
Even on unlimited plans, unreasonable usage may be throttled:
- API calls exceeding 10x your plan's published rate
- Storage consuming resources disproportionate to your plan
- Automated processes creating excessive server load

### Consequences of Violation
1. Warning email with 72-hour cure period
2. Service suspension if not remedied
3. Account termination for repeated violations
4. Legal action for serious violations (hacking, fraud)

## Intellectual Property

### Your Data
- You own all data you store in CloudSync
- CloudSync has license to process data solely to provide services
- We do not analyze your content for advertising
- Your data is not sold to third parties

### CloudSync IP
- Software, platform, and documentation owned by CloudSync Inc.
- Open-source components used under respective licenses
- API responses contain attribution headers where required

## Governing Law and Disputes

### Dispute Resolution
1. Good faith negotiation (30 days)
2. Mediation (if negotiation fails)
3. Binding arbitration (as specified in Terms of Service)
4. Class action waiver applies

### Applicable Law
- US customers: Delaware law governs
- EU customers: English law governs, EU consumer protections apply
- Enterprise contracts: Negotiated jurisdiction

## Contact Information
- General Support: support@cloudsync.io
- Billing: billing@cloudsync.io
- Security: security@cloudsync.io
- Legal: legal@cloudsync.io
- Abuse: abuse@cloudsync.io
- Phone: 1-800-CLOUDSYNC (Mon-Fri 9am-6pm ET)
