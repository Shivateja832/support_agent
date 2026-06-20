# Integration and Webhook Configuration Guide

## Available Integrations

### Native Integrations (No Code Required)
- **Slack**: Get notifications, create records from Slack commands
- **Google Workspace**: Sync files, calendar, and contacts
- **Microsoft 365**: Teams notifications, SharePoint sync
- **Salesforce**: Bidirectional CRM data sync
- **HubSpot**: Marketing and sales data integration
- **Jira**: Issue tracking synchronization
- **GitHub**: Development workflow integration
- **Zapier**: Connect to 5,000+ apps

### Setting Up an Integration
1. Go to Settings → Integrations → Browse Integrations
2. Select the integration you want to add
3. Click "Connect" and authorize CloudSync to access the service
4. Configure which data to sync and sync frequency
5. Test the connection with "Test Integration"
6. Enable automatic sync

## Webhook Configuration

### Creating a Webhook
1. Dashboard → Developer → Webhooks → New Webhook
2. Enter your endpoint URL (must be HTTPS)
3. Select events to subscribe to
4. Set secret key for signature verification
5. Save and test with "Send Test Event"

### Available Webhook Events
**Data Events:**
- `record.created` - New record created
- `record.updated` - Existing record modified
- `record.deleted` - Record soft-deleted
- `record.restored` - Deleted record recovered

**User Events:**
- `user.joined` - New user added to workspace
- `user.removed` - User removed from workspace
- `user.permission_changed` - User role updated

**Billing Events:**
- `subscription.upgraded` - Plan upgraded
- `subscription.downgraded` - Plan downgraded
- `payment.succeeded` - Payment processed
- `payment.failed` - Payment failed

**Sync Events:**
- `sync.started` - Sync operation began
- `sync.completed` - Sync operation finished
- `sync.failed` - Sync encountered error

### Webhook Payload Format
```json
{
  "event": "record.updated",
  "timestamp": "2024-01-15T10:30:00Z",
  "webhook_id": "wh_abc123",
  "data": {
    "record_id": "rec_xyz789",
    "workspace_id": "ws_def456",
    "changes": {
      "field_name": {
        "old_value": "previous",
        "new_value": "updated"
      }
    }
  },
  "signature": "sha256=abc123..."
}
```

### Verifying Webhook Signatures
```python
import hmac
import hashlib

def verify_webhook(payload_body, secret, signature_header):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)
```

### Webhook Best Practices
- Always verify the signature before processing
- Respond with 200 immediately, process asynchronously
- Handle idempotency using the `webhook_id` field
- Implement retry handling (CloudSync retries 5 times)

## REST API Integration

### Base URLs
- Production: https://api.cloudsync.io/v2
- Sandbox: https://sandbox.cloudsync.io/v2

### Common Endpoints
```
GET    /records              List records
POST   /records              Create record
GET    /records/{id}         Get specific record
PATCH  /records/{id}         Update record
DELETE /records/{id}         Delete record

GET    /files                List files
POST   /files/upload         Upload file
GET    /files/{id}/download  Download file

GET    /users                List workspace users
GET    /reports              Available reports
POST   /reports/generate     Generate custom report
```

### SDK Libraries
Official SDKs available for:
- Python: `pip install cloudsync-sdk`
- Node.js: `npm install @cloudsync/sdk`
- Ruby: `gem install cloudsync`
- Go: `go get github.com/cloudsync/go-sdk`
- PHP: `composer require cloudsync/sdk`

### Python SDK Example
```python
from cloudsync import Client

client = Client(api_key="your-api-key")

# List records
records = client.records.list(workspace_id="ws_123", limit=50)

# Create record
new_record = client.records.create({
    "workspace_id": "ws_123",
    "data": {"name": "Example", "status": "active"}
})

# Subscribe to webhooks
client.webhooks.create({
    "url": "https://yourapp.com/webhook",
    "events": ["record.created", "record.updated"]
})
```

## Troubleshooting Integrations

### Integration Not Syncing
1. Check integration status at Settings → Integrations
2. Look for error messages in integration logs
3. Re-authorize the integration (token may have expired)
4. Verify the connected account has required permissions

### Webhook Not Receiving Events
1. Verify endpoint is publicly accessible (not localhost)
2. Check HTTPS is configured correctly
3. Ensure endpoint responds within 5 seconds
4. Review webhook logs at Developer → Webhooks → Logs

### OAuth Token Expired
- OAuth tokens expire after 90 days of inactivity
- Re-connect the integration to get a fresh token
- Use offline_access scope to get long-lived refresh tokens

## Rate Limiting for Integrations
Integration-specific limits:
- Salesforce sync: 100 records/minute
- Jira sync: 50 issues/minute
- Slack notifications: 10/minute per channel
- Webhook delivery: 1,000 events/minute per endpoint
