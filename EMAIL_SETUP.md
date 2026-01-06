# Email Configuration Guide

## Setup Instructions

1. **Create email_config.json** (copy from example):
   ```powershell
   Copy-Item email_config.json.example email_config.json
   ```

2. **Edit email_config.json** with your settings

3. **Get app password** (required for Gmail and most providers)

---

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Visit https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Click "Generate"
4. Copy the 16-character password (remove spaces)  // pragma: allowlist secret

### Step 3: Configure email_config.json
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "youremail@gmail.com",
  "sender_password": "xxxx xxxx xxxx xxxx",  // pragma: allowlist secret
  "recipient_email": "recipient@gmail.com"
}
```

**Note**: Use the app password, NOT your regular Gmail password!

---

## Outlook/Office 365 Setup

```json
{
  "smtp_server": "smtp.office365.com",
  "smtp_port": 587,
  "sender_email": "your-email@outlook.com",
  "sender_password": "your-password",  // pragma: allowlist secret
  "recipient_email": "recipient@example.com"
}
```

---

## Yahoo Mail Setup

```json
{
  "smtp_server": "smtp.mail.yahoo.com",
  "smtp_port": 587,
  "sender_email": "your-email@yahoo.com",
  "sender_password": "your-app-password",  // pragma: allowlist secret
  "recipient_email": "recipient@example.com"
}
```

**Yahoo App Password**: https://login.yahoo.com/account/security

---

## Security Best Practices

### Option 1: Use email_config.json (Simple)
- Already in .gitignore
- Keep email_config.json on local machine only
- NEVER commit to git

### Option 2: Use Environment Variables (Advanced)
Modify run_portfolio_analysis.py to read from env vars instead:
```python
config = {
    'smtp_server': os.getenv('SMTP_SERVER'),
    'sender_email': os.getenv('SENDER_EMAIL'),
    # etc...
}
```

---

## Testing

Test email delivery:
```powershell
python run_portfolio_analysis.py
```

Expected output:
```
✓ Email sent to recipient@example.com
```

---

## Troubleshooting

### "⚠ Email config not found"
**Fix**: Create `email_config.json` from the example file

### "Authentication failed"
**Fix**: Use app password, not regular password (Gmail/Yahoo)

### "SMTPAuthenticationError"
**Fix**:
- Gmail: Enable 2FA and create app password
- Outlook: Use account password
- Yahoo: Generate app password

### "Connection timeout"
**Fix**: Check firewall/antivirus blocking port 587

### "Email not sent after analysis"
**Fix**: Check that PDF was generated in portfolio_results/

---

## Multiple Recipients

To send to multiple people, use comma-separated:
```json
{
  "recipient_email": "person1@example.com, person2@example.com"
}
```

---

## Disable Email

To run analysis without email, simply delete or rename `email_config.json`:
```powershell
Rename-Item email_config.json email_config.json.disabled
```
