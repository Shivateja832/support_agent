# Getting Started: Onboarding Guide for New Users

## Welcome to CloudSync

CloudSync is a collaborative data management and sync platform designed to help teams work more efficiently. This guide will walk you through everything you need to get up and running quickly.

## Step 1: Account Setup (5 minutes)

### Creating Your Workspace
1. Sign up at app.cloudsync.io/signup
2. Choose "Create a new workspace" or "Join an existing workspace"
3. Name your workspace (your company or team name)
4. Choose your primary region (affects data storage location)
5. Select your plan or start with Free tier

### Profile Setup
1. Upload a profile photo (helps teammates identify you)
2. Set your display name and title
3. Add your timezone (affects scheduling features)
4. Connect your preferred notification method

### Securing Your Account
1. Enable Two-Factor Authentication (strongly recommended)
   - Settings → Security → Enable 2FA
   - Use an authenticator app (Google Authenticator, Authy)
2. Save your backup codes securely

## Step 2: Understanding the Interface

### Dashboard Overview
- **Home**: Activity feed and quick access to recent items
- **Data**: Your records, tables, and databases
- **Files**: File storage and sync
- **Reports**: Analytics and custom reports
- **Integrations**: Connect external tools
- **Settings**: Workspace and personal settings

### Navigation Tips
- Use `Ctrl+K` (or `Cmd+K` on Mac) for global search
- Star frequently accessed items for quick access
- Use the activity feed to see recent changes by your team
- Keyboard shortcuts available at Help → Keyboard Shortcuts

## Step 3: Inviting Your Team (Admin Only)

### Sending Invitations
1. Settings → Team → Invite Members
2. Enter email addresses (comma-separated for multiple)
3. Set role for invited members
4. Customize the invitation message
5. Click "Send Invitations"

### Managing Pending Invitations
- Invitations expire after 7 days
- Resend at Settings → Team → Pending Invitations
- Cancel invitations that are no longer needed

### Setting Up Teams/Groups
For larger organizations:
1. Settings → Team → Groups → Create Group
2. Add members to the group
3. Assign permissions at the group level
4. Groups inherit parent group permissions

## Step 4: Importing Your Data

### Import Options
- **CSV Import**: Upload spreadsheet data
- **Excel Import**: .xlsx files supported
- **JSON Import**: Structured data import
- **API Import**: Programmatic data migration
- **Integration Import**: Pull data from connected tools

### CSV Import Process
1. Data → Import → CSV
2. Upload your file
3. Map CSV columns to CloudSync fields
4. Preview the first 10 rows
5. Choose duplicate handling (skip, update, or create)
6. Click Import

### Data Validation
Before importing:
- Ensure date formats are consistent (YYYY-MM-DD recommended)
- Remove special characters from column headers
- Check that required fields are present
- Validate email formats if importing contacts

## Step 5: Setting Up Notifications

### Notification Channels
- **Email**: Daily digest or immediate
- **Slack**: Real-time notifications to channels
- **In-app**: Browser and desktop app notifications
- **Mobile**: Push notifications (install mobile app)

### Configuring Notifications
1. Settings → Notifications
2. Choose which events trigger notifications
3. Set preferred channel per event type
4. Set quiet hours (no notifications during specified times)

## Step 6: Creating Your First Workflow

### Basic Workflow
1. Navigate to Data → Workflows → New Workflow
2. Choose a trigger (e.g., "When record is created")
3. Add conditions (optional, e.g., "Status is Pending")
4. Add actions (e.g., "Send email", "Update field", "Notify team")
5. Test the workflow with sample data
6. Activate the workflow

### Common Workflow Templates
- New customer onboarding notification
- Overdue task reminder
- Status change alert
- Weekly summary report
- Automatic data validation

## Step 7: Mobile App Setup

### Installing the App
- iOS: App Store → Search "CloudSync" → Install
- Android: Play Store → Search "CloudSync" → Install

### Syncing on Mobile
1. Open app and sign in
2. Tap your profile → Workspace Settings
3. Choose sync frequency (Realtime/Hourly/Manual)
4. Enable offline mode if needed (downloads data for offline access)

## Common Questions for New Users

**Q: Can I change my workspace region?**
A: No, region is permanent after data is stored. Choose carefully during setup.

**Q: How many workspaces can I have?**
A: Free: 1, Pro: 3, Business: 10, Enterprise: Unlimited.

**Q: Can I import data from my previous tool?**
A: Yes, we have migration guides for Airtable, Notion, Monday.com, Asana, and others at docs.cloudsync.io/migration.

**Q: Is my data backed up?**
A: Yes, automated daily backups with 30-day retention on all plans.

**Q: How do I cancel my subscription?**
A: Settings → Billing → Manage Plan → Cancel Subscription. Access continues until period end.

## Getting Help
- **Documentation**: docs.cloudsync.io
- **Video Tutorials**: learn.cloudsync.io
- **Community Forum**: community.cloudsync.io
- **Support**: support@cloudsync.io or in-app chat
- **Status Page**: status.cloudsync.io
