# Billing, Payments, and Subscription Management

## Subscription Plans

### Free Tier
- Up to 3 users
- 5GB storage
- 100 API calls/hour
- Community support only
- No credit card required

### Pro Plan ($49/month per workspace)
- Up to 25 users
- 100GB storage
- 1,000 API calls/hour
- Priority email support (24hr response)
- Advanced analytics
- Custom integrations

### Business Plan ($149/month per workspace)
- Up to 100 users
- 500GB storage
- 10,000 API calls/hour
- Phone and email support (4hr response)
- SLA: 99.9% uptime guarantee
- Dedicated success manager

### Enterprise Plan (Custom Pricing)
- Unlimited users
- Unlimited storage
- Unlimited API calls
- 24/7 dedicated support
- SLA: 99.99% uptime
- Custom contracts and invoicing
- On-premise deployment option

## Payment Methods

### Accepted Payments
- Credit/Debit cards (Visa, Mastercard, American Express)
- PayPal
- Wire transfer (Enterprise only)
- Purchase orders (Enterprise only)
- Annual billing with 20% discount

### Updating Payment Information
1. Go to Billing → Payment Methods
2. Click "Add Payment Method"
3. Enter card details
4. Set as default payment method
5. Remove old payment method if desired

### Failed Payments
**What happens when payment fails:**
- Day 1: First payment attempt fails, email notification sent
- Day 3: Second attempt, grace period begins
- Day 7: Third attempt, service degraded to read-only
- Day 14: Account suspended, data retained for 30 days
- Day 44: Account deleted (30-day retention window)

**Resolving Failed Payments:**
1. Update payment method in Billing settings
2. Contact your bank if card is being declined
3. Contact support for manual payment processing

## Refund Policy

### Refund Eligibility
- Monthly plans: Refund within 7 days of charge
- Annual plans: Prorated refund within 30 days of payment
- No refunds after the stated period
- Service credits for downtime exceeding SLA

### Requesting a Refund
1. Email billing@cloudsync.io within the refund window
2. Include: Account email, charge date, reason for refund
3. Processing time: 5-10 business days to original payment method

## Invoice and Tax

### Accessing Invoices
- Billing → Invoice History
- All invoices available for download as PDF
- Sent automatically on billing date to billing contact email

### Tax Exemption
- Submit tax exemption certificate at Billing → Tax Settings
- Processing takes 1-3 business days
- Applied to future invoices only

### Business Information
Update business name and address at Billing → Business Information for accurate invoices.

## Upgrading and Downgrading

### Upgrading
- Effective immediately
- Prorated charge for remainder of billing period
- New features available instantly

### Downgrading
- Effective at end of current billing period
- Will lose access to premium features
- Data may need to be reduced to fit new storage limits
- Warning shown if current usage exceeds new plan limits

## Usage and Overage

### Storage Overage
- 10GB overage: Included buffer (no charge)
- Beyond buffer: $0.10/GB/month
- Alert emails at 80% and 95% of limit

### API Overage
- Requests beyond limit are queued, not rejected
- Overage rate: $0.001 per additional request
- Option to hard-cap at limit (requests rejected instead)
