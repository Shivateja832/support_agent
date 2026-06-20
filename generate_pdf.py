#!/usr/bin/env python3
"""Generate PDF knowledge base document for CloudSync Support"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path

def create_troubleshooting_pdf():
    output_file = Path(__file__).parent / "data" / "cloudsync_troubleshooting_handbook.pdf"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=24, textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=20, alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        'CustomH1', parent=styles['Heading1'],
        fontSize=16, textColor=colors.HexColor('#1e3a5f'),
        spaceBefore=16, spaceAfter=8,
        borderPad=4
    )
    h2_style = ParagraphStyle(
        'CustomH2', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#2c5f8a'),
        spaceBefore=12, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, leading=16, spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontSize=10, leading=16, leftIndent=20,
        bulletIndent=10, spaceAfter=4
    )
    code_style = ParagraphStyle(
        'Code', parent=styles['Code'],
        fontSize=9, backColor=colors.HexColor('#f4f4f4'),
        leftIndent=20, rightIndent=20, borderPad=6,
        leading=14
    )
    note_style = ParagraphStyle(
        'Note', parent=styles['Normal'],
        fontSize=10, leading=16, leftIndent=15,
        textColor=colors.HexColor('#8B4513'),
        backColor=colors.HexColor('#FFF8DC'),
        borderPad=8
    )

    story = []

    # Title
    story.append(Paragraph("CloudSync", title_style))
    story.append(Paragraph("Complete Troubleshooting Handbook", title_style))
    story.append(Paragraph("Version 3.2 | Support Reference Document", ParagraphStyle(
        'sub', parent=styles['Normal'], alignment=TA_CENTER,
        fontSize=11, textColor=colors.grey, spaceAfter=30
    )))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 20))

    # Table of Contents note
    story.append(Paragraph("About This Document", h1_style))
    story.append(Paragraph(
        "This handbook is the official troubleshooting reference for CloudSync Support Representatives "
        "and technically proficient customers. It covers the most common issues across all product areas "
        "with step-by-step resolution guides, diagnostic commands, and escalation criteria.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Section 1: Login & Authentication
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("Section 1: Login and Authentication Issues", h1_style))

    story.append(Paragraph("1.1 Cannot Log In - Checklist", h2_style))
    checklist = [
        ("Step 1", "Verify the email address is correct — check for typos, extra spaces"),
        ("Step 2", "Confirm Caps Lock is not enabled when entering password"),
        ("Step 3", "Try password reset via the 'Forgot Password' link"),
        ("Step 4", "Clear browser cookies and cache, then retry"),
        ("Step 5", "Try a different browser or incognito/private window"),
        ("Step 6", "Check for account lockout (5 failed attempts triggers lockout)"),
        ("Step 7", "Wait 15 minutes if temporarily locked out"),
        ("Step 8", "Contact support if issue persists after all above steps"),
    ]
    for step, description in checklist:
        story.append(Paragraph(f"• <b>{step}</b>: {description}", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1.2 Two-Factor Authentication Problems", h2_style))
    story.append(Paragraph(
        "If a user cannot complete 2FA verification, follow this resolution path:",
        body_style
    ))
    story.append(Paragraph("• User has authenticator app but code not working:", bullet_style))
    story.append(Paragraph("  - Check device time sync (most common cause — TOTP requires accurate time)", bullet_style))
    story.append(Paragraph("  - Android: Settings → General Management → Date and Time → Automatic", bullet_style))
    story.append(Paragraph("  - iOS: Settings → General → Date & Time → Set Automatically", bullet_style))
    story.append(Paragraph("• User has backup codes: Use one backup code to log in, then re-setup 2FA", bullet_style))
    story.append(Paragraph("• User has no backup codes and no authenticator access: Requires identity verification via support", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.3 SSO/SAML Authentication Failures", h2_style))
    story.append(Paragraph(
        "Enterprise SSO errors require coordination between the customer's IT team and CloudSync. "
        "Common SAML error codes and their meanings:",
        body_style
    ))
    
    # Error table
    error_data = [
        ['Error Code', 'Meaning', 'Resolution'],
        ['SAML_INVALID_SIGNATURE', 'Certificate mismatch', 'Re-upload IdP metadata certificate'],
        ['SAML_EXPIRED_RESPONSE', 'Clock skew > 5 minutes', 'Sync server time on IdP'],
        ['SAML_NO_ATTRIBUTE', 'Required attribute missing', 'Map email attribute in IdP config'],
        ['SAML_INVALID_RECIPIENT', 'Wrong ACS URL', 'Update ACS URL in IdP to match CloudSync'],
        ['USER_NOT_PROVISIONED', 'User not in SCIM', 'Add user to provisioning group in IdP'],
    ]
    t = Table(error_data, colWidths=[2.2*inch, 2*inch, 2.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Section 2: Data and Sync
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("Section 2: Data Sync and Recovery", h1_style))

    story.append(Paragraph("2.1 Sync Failure Diagnostic Tree", h2_style))
    story.append(Paragraph(
        "Use this decision tree to diagnose sync failures systematically:",
        body_style
    ))
    diag_steps = [
        "Is the sync status indicator green, yellow, or red?",
        "→ GREEN: Sync is working. Perceived issue may be user error or UI caching.",
        "→ YELLOW: Sync is delayed. Check status.cloudsync.io for ongoing incidents.",
        "→ RED: Sync stopped. Proceed to step 2.",
        "Is the device connected to the internet?",
        "→ NO: Reconnect to internet. Offline changes will sync automatically.",
        "→ YES: Proceed to step 3.",
        "Use 'Force Sync' (Ctrl+Shift+S / Cmd+Shift+S). Does sync complete?",
        "→ YES: Intermittent issue resolved. Monitor for recurrence.",
        "→ NO: Check sync error logs at Dashboard → Developer → Sync Logs.",
        "Are there error messages in sync logs?",
        "→ AUTH_ERROR: API key may have expired. Regenerate at Settings → API Keys.",
        "→ QUOTA_EXCEEDED: Storage limit reached. Upgrade plan or free up space.",
        "→ CONFLICT_LOOP: Contact support — manual conflict resolution required.",
        "→ No errors but sync not working: Escalate to Tier 2 support.",
    ]
    for step in diag_steps:
        indent = "  " if step.startswith("→") else ""
        style = bullet_style if step.startswith("→") else body_style
        story.append(Paragraph(f"{indent}{step}", style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.2 Data Recovery Procedures", h2_style))
    story.append(Paragraph(
        "<b>IMPORTANT:</b> Always confirm with the customer what data is missing before attempting recovery. "
        "Incorrect recovery can overwrite newer data.",
        note_style
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Recovery Option 1 — Trash Recovery (0-30 days):", h2_style))
    story.append(Paragraph("• Navigate to Data → Trash", bullet_style))
    story.append(Paragraph("• Search for the deleted record by name or date", bullet_style))
    story.append(Paragraph("• Click Restore to return to original location", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Recovery Option 2 — Version History:", h2_style))
    story.append(Paragraph("• Open the affected record", bullet_style))
    story.append(Paragraph("• Click History tab on the right sidebar", bullet_style))
    story.append(Paragraph("• Browse versions with timestamp and editor info", bullet_style))
    story.append(Paragraph("• Click Restore on any version to roll back", bullet_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Recovery Option 3 — Backup Restore (Enterprise Only):", h2_style))
    story.append(Paragraph("• Contact Enterprise support for point-in-time restore", bullet_style))
    story.append(Paragraph("• Provide: workspace ID, target restore time, scope of data", bullet_style))
    story.append(Paragraph("• Estimated restoration time: 2-4 hours depending on data volume", bullet_style))

    story.append(Spacer(1, 15))

    # Section 3: API and Integrations
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("Section 3: API and Integration Troubleshooting", h1_style))

    story.append(Paragraph("3.1 API Error Code Reference", h2_style))
    api_errors = [
        ['HTTP Code', 'Error Type', 'Most Common Cause', 'Resolution'],
        ['400', 'Bad Request', 'Invalid JSON or missing required field', 'Validate request body against API docs'],
        ['401', 'Unauthorized', 'Invalid or expired API key', 'Regenerate API key, check Authorization header'],
        ['403', 'Forbidden', 'Insufficient permissions', 'Check API key permissions or user role'],
        ['404', 'Not Found', 'Wrong endpoint or deleted resource', 'Verify endpoint URL and resource existence'],
        ['409', 'Conflict', 'Duplicate unique field value', 'Check for existing record, use PATCH instead of POST'],
        ['422', 'Unprocessable', 'Validation failure on field value', 'Check field format requirements in API docs'],
        ['429', 'Rate Limited', 'Too many requests', 'Implement backoff, reduce request frequency'],
        ['500', 'Server Error', 'CloudSync internal error', 'Retry with backoff, report if persistent'],
        ['503', 'Unavailable', 'Service maintenance or overload', 'Check status page, retry after Retry-After header'],
    ]
    t2 = Table(api_errors, colWidths=[0.8*inch, 1.3*inch, 2.2*inch, 2.7*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c5f8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f4f8')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    story.append(Paragraph("3.2 Debugging API Calls", h2_style))
    story.append(Paragraph("Use these curl commands for quick API debugging:", body_style))
    story.append(Paragraph(
        "# Test authentication\n"
        "curl -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
        "  https://api.cloudsync.io/v2/me\n\n"
        "# Test with verbose output\n"
        "curl -v -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
        "  https://api.cloudsync.io/v2/records?limit=1\n\n"
        "# Test with timing info\n"
        "curl -w '@curl-format.txt' -H 'Authorization: Bearer KEY' \\\n"
        "  https://api.cloudsync.io/v2/health",
        code_style
    ))
    story.append(Spacer(1, 10))

    # Section 4: Escalation Guide
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("Section 4: Escalation Guide", h1_style))

    story.append(Paragraph("4.1 When to Escalate", h2_style))
    escalation_triggers = [
        ("Tier 1 → Tier 2", [
            "Issue not resolved after following all standard troubleshooting steps",
            "Customer reports data loss or corruption",
            "Authentication/SSO failure not resolved by re-authorization",
            "Sync errors persisting after Force Sync and cache clear",
            "Customer requests access to audit logs beyond their plan",
        ]),
        ("Tier 2 → Engineering", [
            "Suspected bug with reproducible steps",
            "Performance degradation without clear cause",
            "Data inconsistency that cannot be explained",
            "Security incident or suspected breach",
            "Infrastructure-level issues not shown on status page",
        ]),
        ("Any Tier → Legal/Finance", [
            "Customer mentions legal action or regulatory investigation",
            "Billing disputes exceeding $1,000",
            "GDPR data deletion or access requests",
            "Requests for compliance documentation with NDA",
            "Subpoena or law enforcement requests",
        ]),
    ]
    for tier, triggers in escalation_triggers:
        story.append(Paragraph(f"<b>{tier}:</b>", ParagraphStyle('bold', parent=body_style, textColor=colors.HexColor('#1e3a5f'))))
        for trigger in triggers:
            story.append(Paragraph(f"• {trigger}", bullet_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("4.2 Escalation Handoff Checklist", h2_style))
    handoff_items = [
        "Customer name, account email, workspace ID",
        "Plan type and contract details",
        "Clear description of the issue with exact error messages",
        "Steps already attempted and their results",
        "Customer's urgency level and business impact",
        "Any screenshots or screen recordings shared by customer",
        "API request IDs for technical issues",
        "Timeline of when issue started",
        "Whether issue is affecting all users or specific ones",
        "Customer's preferred contact method for follow-up",
    ]
    for item in handoff_items:
        story.append(Paragraph(f"☐ {item}", bullet_style))
    story.append(Spacer(1, 20))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "CloudSync Internal Support Reference | Confidential | Last Updated: January 2025 | "
        "Questions: support-team@cloudsync.io",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                      textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("PDF created successfully!")

if __name__ == "__main__":
    create_troubleshooting_pdf()
