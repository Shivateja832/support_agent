# API Authentication Guide

## Overview
This document covers all aspects of API authentication for CloudSync SaaS platform, including OAuth 2.0, API keys, JWT tokens, and common troubleshooting steps.

## Authentication Methods

### 1. API Key Authentication
API keys are the simplest form of authentication. Each key is associated with a specific account and set of permissions.

**Generating an API Key:**
1. Log in to your CloudSync dashboard
2. Navigate to Settings → API Keys
3. Click "Generate New Key"
4. Set permissions (Read, Write, Admin)
5. Copy and store the key securely — it won't be shown again

**Usage:**
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Rate Limits:**
- Free tier: 100 requests/hour
- Pro tier: 1,000 requests/hour
- Enterprise: Unlimited with fair use policy

### 2. OAuth 2.0
OAuth 2.0 is required for user-facing integrations.

**Authorization Flow:**
1. Redirect user to: `https://api.cloudsync.io/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=read write`
2. User grants permission
3. Receive authorization code at your redirect URI
4. Exchange code for access token: POST to `https://api.cloudsync.io/oauth/token`
5. Use access token in Authorization header

**Token Expiry:**
- Access tokens expire after 1 hour
- Refresh tokens expire after 30 days
- Use refresh token to obtain new access token without re-authorization

### 3. JWT Tokens
JWT tokens are used for service-to-service authentication.

**Token Structure:**
- Header: Algorithm and token type
- Payload: Claims (user ID, expiry, permissions)
- Signature: Verified with your secret key

## Common Authentication Errors

### Error 401: Unauthorized
**Causes:**
- Invalid or expired API key
- Missing Authorization header
- Incorrect token format

**Resolution:**
1. Verify the API key is correct and active
2. Check the Authorization header format: `Bearer <token>`
3. Regenerate the API key if suspected compromise
4. Ensure the key has appropriate permissions for the operation

### Error 403: Forbidden
**Causes:**
- Valid authentication but insufficient permissions
- IP allowlist restriction
- Account suspended or downgraded

**Resolution:**
1. Check your account's permission level
2. Review IP allowlist settings in Security → Access Control
3. Contact billing if account status is the issue

### Error 429: Rate Limit Exceeded
**Causes:**
- Exceeded request quota for your tier

**Resolution:**
1. Implement exponential backoff
2. Cache responses where possible
3. Upgrade your plan for higher limits
4. Contact support for temporary limit increases

## Security Best Practices
- Never commit API keys to version control
- Rotate API keys every 90 days
- Use environment variables for key storage
- Enable IP allowlisting for production keys
- Monitor API key usage in the dashboard

## Logs and Debugging
Access API logs at: Dashboard → Developer → API Logs
Logs include: timestamp, endpoint, status code, response time, IP address
Retention: 30 days for Pro, 90 days for Enterprise
