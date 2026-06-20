# Network Configuration and Connectivity Guide

## Network Requirements

### Minimum Bandwidth Requirements
- Web app: 1 Mbps download, 0.5 Mbps upload
- Desktop app with file sync: 5 Mbps download, 2 Mbps upload
- Video collaboration features: 10 Mbps bidirectional
- Enterprise real-time sync: 25 Mbps recommended

### Required Ports and Protocols
All CloudSync communication uses HTTPS (port 443). No custom ports required.

WebSocket connections used for real-time features:
- wss://realtime.cloudsync.io (port 443)
- Fallback: Long-polling over HTTPS if WebSocket blocked

### Firewall Configuration
Allow outbound connections to:
- *.cloudsync.io (all subdomains)
- *.cloudfront.net (CDN)
- *.amazonaws.com (infrastructure)

IP ranges for strict allowlist environments:
Contact support@cloudsync.io for current IP range list (updated quarterly).

## Proxy Configuration

### HTTP Proxy
Configure in Desktop App:
Settings → Advanced → Network → HTTP Proxy
Enter: http://proxy-server:port

### NTLM/Kerberos Authentication
Enterprise proxy authentication supported.
Contact IT team for proxy credentials configuration.

### SSL Inspection
If your organization uses SSL inspection (HTTPS decryption):
1. Add CloudSync root certificate exception
2. Or install your organization's CA certificate in the desktop app
Settings → Advanced → Security → Custom CA Certificate

## VPN Considerations

### Split Tunneling
Recommend excluding CloudSync from VPN tunnel for best performance:
- *.cloudsync.io
- *.cloudfront.net

### VPN and SSO
If your SSO provider is behind a VPN:
- Users must connect to VPN before authenticating
- Contact your IT admin for VPN-aware SSO configuration
- CloudSync supports conditional access policies via Azure AD and Okta

## DNS Configuration

### DNS Requirements
CloudSync requires reliable DNS resolution.
Test: `nslookup api.cloudsync.io`
Expected: IP in AWS range (3.x.x.x or 52.x.x.x)

### DNS-over-HTTPS
CloudSync is compatible with DoH configurations.
If experiencing DNS issues, try flushing DNS cache:
- Windows: `ipconfig /flushdns`
- Mac: `sudo dscacheutil -flushcache`
- Linux: `sudo systemd-resolve --flush-caches`

## Offline Functionality

### What Works Offline
- View cached data (last sync snapshot)
- Edit records (synced when reconnected)
- View downloaded files
- Access saved reports

### What Requires Internet
- Real-time collaboration
- File uploads
- Authentication (login)
- Integration data pulls
- Sending notifications

### Conflict Resolution on Reconnect
When offline edits sync:
1. CloudSync checks for server-side changes
2. Timestamp-based conflict detection
3. Conflicts presented for manual resolution or auto-resolved by "Last Write Wins"
4. Notification sent for each resolved conflict

## CDN and Performance

### Global CDN
CloudSync uses CloudFront CDN with 450+ edge locations globally.
Static assets served from nearest edge for fast load times.

### Regional Endpoints
Connect to your nearest region for lowest latency:
- api-us-east.cloudsync.io
- api-us-west.cloudsync.io
- api-eu-west.cloudsync.io
- api-eu-central.cloudsync.io
- api-ap-southeast.cloudsync.io
- api-ap-south.cloudsync.io

### Latency Benchmarks
Expected response times by region:
- Same region: 20-50ms
- Cross-region (same continent): 50-150ms
- Cross-continent: 150-300ms

## Monitoring and Diagnostics

### Built-in Network Diagnostics
In the desktop app: Help → Run Diagnostics
Tests: DNS resolution, HTTPS connectivity, WebSocket, latency

### Network Monitoring Integration
CloudSync supports SNMP traps for enterprise network monitoring.
Contact your Customer Success Manager for configuration.

## Corporate Network Troubleshooting

### "Connection Failed" Error
1. Verify internet connectivity: ping 8.8.8.8
2. Verify DNS: nslookup cloudsync.io
3. Test HTTPS: curl https://status.cloudsync.io/api/health
4. Check firewall logs for blocked requests
5. Disable VPN temporarily to isolate issue

### Slow Sync on Corporate Network
1. Check if QoS policies are throttling CloudSync traffic
2. Verify proxy server isn't causing extra latency
3. Try direct connection (bypass proxy temporarily to test)
4. Check for packet inspection adding overhead

### WebSocket Connection Issues
Real-time features require WebSockets.
If WebSockets are blocked by corporate firewall:
1. CloudSync automatically falls back to long-polling
2. Performance may be reduced but functionality maintained
3. Request IT to allow WSS connections to *.cloudsync.io
