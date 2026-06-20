# Data Synchronization Troubleshooting

## How CloudSync Data Sync Works

### Sync Architecture
CloudSync uses a real-time event-driven sync architecture:
1. Client makes a change (create/update/delete)
2. Change is written to primary database
3. Event published to message queue (Kafka)
4. Sync service processes event
5. Change propagated to all connected clients and services
6. Confirmation sent back to originating client

### Sync Modes
- **Real-time**: Changes reflected within 1-3 seconds
- **Near-real-time**: Changes reflected within 30 seconds (used during high load)
- **Batch sync**: Scheduled sync every 15 minutes (fallback mode)
- **Manual sync**: User-triggered, available as "Force Sync" button

## Common Sync Issues

### Data Not Syncing

**Symptoms:**
- Changes made on one device not appearing on another
- Old data showing despite updates
- Missing records

**Diagnostic Steps:**

1. **Check Sync Status Indicator**
   - Green circle: Syncing normally
   - Yellow circle: Sync delayed (within 5 minutes)
   - Red circle: Sync stopped (action required)
   - Grey circle: Offline mode

2. **Check Internet Connectivity**
   - Sync requires active internet connection
   - Offline changes are queued and sync when reconnected

3. **Review Sync Logs**
   Dashboard → Developer → Sync Logs
   Look for: Error events, conflict markers, dropped events

4. **Force Sync**
   - Desktop app: Ctrl+Shift+S (Windows/Linux), Cmd+Shift+S (Mac)
   - Web app: Profile icon → Force Sync
   - Mobile app: Pull down to refresh on main screen

### Sync Conflicts

**What Causes Conflicts:**
- Same record edited on multiple devices while offline
- Simultaneous edits by multiple users

**Conflict Resolution Policy:**
CloudSync uses "Last Write Wins" by default:
- The most recent change (by timestamp) is kept
- Previous version saved as conflict copy

**Viewing Conflicts:**
Dashboard → Data → Conflict Resolution Center
- Shows all conflicts from last 30 days
- Option to manually choose which version to keep
- Merge option for text fields (Pro and above)

**Custom Conflict Resolution (Enterprise):**
Contact your success manager to configure:
- Field-level merge strategies
- User-role-based resolution priority
- Custom conflict webhooks

### Partial Sync

**Symptoms:**
- Some records syncing, others not
- Certain fields not updating

**Common Causes:**
- Permission restrictions (user may not have access to certain records)
- Field-level validation failures blocking sync
- Storage quota exceeded

**Resolution:**
1. Check storage usage at Settings → Storage
2. Verify user permissions at Settings → Team → Permissions
3. Review field validation rules at Settings → Data → Validation

## File Sync Specific Issues

### Large File Uploads Failing
- Maximum file size: 2GB per file
- Recommended: Use chunked upload for files >100MB
- Chunked upload endpoint: POST /api/files/chunked/init

### File Sync Speed
Factors affecting upload speed:
- Your internet connection bandwidth
- File size and quantity
- Current server load

Optimization tips:
- Upload during off-peak hours (10pm-6am local time)
- Use the desktop client (more efficient than web browser)
- Enable compression for text-based files

## Real-Time Collaboration Sync

### Live Co-editing
- Supported in: Documents, Spreadsheets, Presentations
- Maximum concurrent editors: 50 (Pro), 200 (Enterprise)
- Operational Transformation used to merge concurrent edits

### Presence Features
- See who's viewing the same document in real-time
- Cursor positions shown for active editors
- "Someone is typing..." indicators

## Mobile App Sync

### Background Sync Settings
- iPhone: Settings → CloudSync → Background App Refresh → Enable
- Android: Battery → CloudSync → Allow Background Activity → Enable
- Low Power Mode may disable background sync

### Offline Mode
- Edits made offline are queued locally
- Syncs automatically when connection restored
- Conflict detection applies when reconnected

## API Sync Operations

### Polling vs Webhooks
**Polling (less efficient):**
```
GET /api/changes?since=2024-01-01T00:00:00Z&limit=100
```

**Webhooks (recommended):**
Register at Dashboard → Developer → Webhooks
Events: `record.created`, `record.updated`, `record.deleted`, `sync.completed`

### Bulk Sync Operations
```
POST /api/sync/bulk
{
  "operations": [
    {"type": "upsert", "record": {...}},
    {"type": "delete", "id": "rec_123"}
  ]
}
```
Limit: 1,000 operations per request
Async mode available for larger batches

## Data Integrity and Recovery

### Deleted Data Recovery
- Soft-deleted records recoverable within 30 days
- Dashboard → Data → Trash → Restore
- Permanent deletion after 30-day window

### Version History
- Pro plan: 30-day version history
- Business plan: 90-day version history
- Enterprise: Unlimited version history
- Access at: Any record → History tab

### Data Export for Recovery
If sync is severely broken, export data:
Settings → Data → Export → Choose format (CSV, JSON, Excel)
