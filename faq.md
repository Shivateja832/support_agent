# Frequently Asked Questions (FAQ)

## General Questions

**Q: What is CloudSync?**
A: CloudSync is a cloud-based data management and collaboration platform that allows teams to sync, store, and work with data in real-time. It combines the flexibility of a database, the simplicity of a spreadsheet, and powerful automation capabilities.

**Q: Is CloudSync suitable for my industry?**
A: CloudSync is used across industries including: Technology, Healthcare (HIPAA compliant), Finance, Retail, Manufacturing, Education, and Non-profits. The flexible data model adapts to virtually any use case.

**Q: Can CloudSync replace my existing spreadsheet or database tools?**
A: CloudSync can replace spreadsheets for collaborative use cases and light databases. For complex relational databases or high-transaction systems, CloudSync integrates alongside your existing tools rather than replacing them.

**Q: What languages does the interface support?**
A: English, Spanish, French, German, Japanese, Chinese (Simplified and Traditional), Portuguese, Italian, Dutch, Korean, Arabic, and Hindi.

## Account and Billing Questions

**Q: Can I try CloudSync before buying?**
A: Yes! The Free tier is available indefinitely with no credit card required. Pro and Business plans have 14-day free trials.

**Q: What happens to my data if I downgrade?**
A: Your data is preserved but access may be limited based on the new plan. You'll receive warnings about which features will be restricted.

**Q: Can I switch from monthly to annual billing?**
A: Yes, switch at any time at Settings → Billing. Annual billing saves 20%. The difference is prorated for your current period.

**Q: Do you offer discounts for nonprofits or education?**
A: Yes! Nonprofits receive 50% discount, educational institutions receive 30% discount. Apply at cloudsync.io/nonprofit or cloudsync.io/education.

**Q: Can I get a custom contract?**
A: Enterprise customers can arrange custom contracts with specific terms, payment schedules, and SLAs. Contact sales@cloudsync.io.

## Data and Privacy Questions

**Q: Where is my data stored?**
A: By default, US customers' data is stored in US East (Virginia). You can choose your region when creating a workspace. See the Data Residency section of our Security Policy for all available regions.

**Q: Does CloudSync access my data?**
A: CloudSync support staff may access data when you explicitly grant access for troubleshooting. Otherwise, your data is processed only to provide the service. We never analyze content for advertising.

**Q: How do I export all my data?**
A: Settings → Data → Export All Data. Choose format (CSV, JSON, XML) and all your data will be prepared for download within 24 hours.

**Q: Is CloudSync GDPR compliant?**
A: Yes. CloudSync is fully GDPR compliant. Data Processing Agreements (DPAs) available upon request. Your privacy rights (access, deletion, portability) are supported.

**Q: What happens to my data if I cancel?**
A: Data is retained for 30 days after cancellation, then permanently deleted. Export your data before canceling if you need it.

## Technical Questions

**Q: What browsers does CloudSync support?**
A: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+. Internet Explorer is not supported.

**Q: Does CloudSync have a mobile app?**
A: Yes, iOS (iOS 14+) and Android (Android 8+) apps are available. Mobile apps support offline mode for working without internet.

**Q: Is there a desktop application?**
A: Yes, desktop apps for Mac (macOS 11+) and Windows (Windows 10+) are available. The desktop app syncs files in the background and provides better performance.

**Q: What's the maximum file size I can upload?**
A: Individual files up to 2GB. For larger files, use the chunked upload API. Total storage depends on your plan.

**Q: Does CloudSync have an API?**
A: Yes, a comprehensive REST API is available. Documentation at docs.cloudsync.io/api. SDK available for Python, JavaScript, Ruby, Go, and PHP.

**Q: Can CloudSync connect to my database?**
A: Yes, through our database integration feature (Business and Enterprise plans): PostgreSQL, MySQL, Microsoft SQL Server, Oracle, and MongoDB.

## Support and Service Questions

**Q: How do I contact support?**
A: Email: support@cloudsync.io | Live chat in the app | Phone: 1-800-CLOUDSYNC (Business hours, Mon-Fri 9am-6pm ET)

**Q: What's the difference between support tiers?**
A: Free: Community support only. Pro: Email and chat with 24-hour response. Business: Phone support with 4-hour response. Enterprise: 24/7 dedicated support with 15-minute response for critical issues.

**Q: How do I report a bug?**
A: Report bugs at support@cloudsync.io or through the in-app feedback button (? icon at bottom right). Include: steps to reproduce, expected behavior, actual behavior, browser/OS info, and screenshots if possible.

**Q: Is there a status page?**
A: Yes, status.cloudsync.io shows real-time service status and incident history. Subscribe for email alerts.

**Q: Where can I find the roadmap?**
A: Public roadmap at cloudsync.io/roadmap. Vote on features and submit your own ideas at community.cloudsync.io.

## Collaboration Questions

**Q: How many people can work on a document simultaneously?**
A: Pro: Up to 50 concurrent editors. Business: Up to 100. Enterprise: Up to 200.

**Q: Can external users (non-workspace members) collaborate?**
A: Yes, share items with guest access. Guests have view-only or comment-only access and don't consume a user seat.

**Q: Is there a chat or messaging feature?**
A: Comments are available on any record or document. For team messaging, we integrate with Slack, Teams, and other messaging platforms. A native messaging feature is on our roadmap.

**Q: Can I set permissions at the record level?**
A: Record-level permissions are available on Business and Enterprise plans. Pro plans support field-level visibility.

## Troubleshooting Quick Reference

**Can't log in:**
→ Try password reset, check for account lockout, clear browser cookies

**Sync not working:**
→ Check internet connection, look for sync status indicator, use Force Sync option

**Slow performance:**
→ Check status.cloudsync.io, switch to nearest regional endpoint, enable browser caching

**Webhook not working:**
→ Verify HTTPS endpoint, check endpoint responds within 5 seconds, review webhook logs

**Import failing:**
→ Check CSV format, ensure required fields present, look for special characters in headers

**Integration disconnected:**
→ Re-authorize the integration, check connected account hasn't been deleted or had password changed
