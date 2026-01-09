# Portfolio Analyser - Email Automation Setup

## Overview
Automatically run portfolio analysis every morning and receive results via email.

## Prerequisites
- Python 3.14.2 (already installed)
- Portfolio Analyser project (already setup)
- Gmail account with App Password (see Gmail Setup below)

---

## Step 1: Gmail Setup (5 minutes)

### Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow prompts to enable (if not already enabled)

### Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Windows Computer"
4. Click "Generate"
5. **Copy the 16-character password** (you won't see it again)

### Configure Email Settings
Edit `config/email_config.json`:
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "xxxx xxxx xxxx xxxx",  <-- Paste your App Password here
  "recipient_email": "your-email@gmail.com",
  "subject_prefix": "Portfolio Analysis"
}
```

---

## Step 2: Test Email Sending (2 minutes)

Open PowerShell in `c:\workspace\portfolio_analyser`:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Test email sending
python src/run_portfolio_analysis.py --email
```

**Expected output:**
```
[OK] Email sent successfully to your-email@gmail.com
```

**If you see errors:**
- `Authentication failed`: Check App Password (no spaces, 16 characters)
- `SMTP connection error`: Check firewall/antivirus blocking port 587
- `File not found`: Make sure email_config.json exists in config/

---

## Step 3: Windows Task Scheduler Setup (10 minutes)

### Option A: Automated Script (Recommended)

Run the setup script:
```powershell
.\scripts\setup_automation.ps1
```

This creates a scheduled task that runs **every day at 9:00 AM**.

### Option B: Manual Setup

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create New Task:**
   - Click "Create Task" (not "Create Basic Task")
   - Name: `Portfolio Analyser - Daily Report`
   - Description: `Run portfolio analysis and email results`
   - Check: "Run whether user is logged on or not"
   - Check: "Run with highest privileges"

3. **Triggers Tab:**
   - Click "New..."
   - Begin the task: "On a schedule"
   - Settings: "Daily"
   - Start: Choose today's date, **9:00:00 AM**
   - Recur every: 1 days
   - Enabled: ✅
   - Click "OK"

4. **Actions Tab:**
   - Click "New..."
   - Action: "Start a program"
   - Program/script: `C:\workspace\portfolio_analyser\.venv\Scripts\python.exe`
   - Arguments: `src/run_portfolio_analysis.py --email`
   - Start in: `C:\workspace\portfolio_analyser`
   - Click "OK"

5. **Conditions Tab:**
   - ✅ Start only if computer is on AC power
   - ✅ Wake the computer to run this task
   - ❌ Stop if the computer switches to battery power

6. **Settings Tab:**
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after scheduled start is missed
   - ❌ Stop the task if it runs longer than: 3 hours
   - If running task does not end when requested: "Stop existing instance"
   - Click "OK"

7. **Save Task:**
   - You'll be prompted for your Windows password
   - Enter password and click "OK"

---

## Step 4: Test Scheduled Task (2 minutes)

### Run Task Manually:
1. Open Task Scheduler (`taskschd.msc`)
2. Find: `Portfolio Analyser - Daily Report`
3. Right-click → "Run"
4. Watch "Status" column → should show "Running" then "Ready"
5. Check your email inbox (within 1-2 minutes)

**Expected email:**
- Subject: `Portfolio Analysis - 2026-01-09 09:00`
- Attachments: PDF report, Excel tracker
- Body: Summary of holdings and signals

### View Task History:
1. Right-click task → "Properties"
2. Click "History" tab
3. Look for "Task Started" and "Task Completed" events

**If task fails:**
- Check "Last Run Result" column (code 0x0 = success)
- View History tab for error details
- Common issues:
  - Path errors: Verify paths in Actions tab
  - Permission errors: Ensure "Run with highest privileges" is checked
  - Python not found: Use full path to python.exe

---

## Step 5: Verify Daily Operation (1 day)

Wait until tomorrow at 9:00 AM and check:
- ✅ Email received at 9:00 AM
- ✅ PDF shows today's date
- ✅ Excel tracker updated
- ✅ Task history shows successful completion

---

## Customization Options

### Change Run Time:
Edit the task trigger:
- 6:00 AM (before work)
- 4:00 PM (market close)
- 9:00 PM (evening review)

### Run on Weekdays Only:
In Triggers tab, change "Daily" to "Weekly" and select Mon-Fri.

### Add Multiple Recipients:
Edit `email_config.json`:
```json
"recipient_email": "you@gmail.com, spouse@gmail.com"
```

### Customize Email Subject:
Edit `email_config.json`:
```json
"subject_prefix": "📊 Portfolio Update"
```

---

## Troubleshooting

### "Task is not running"
- Check Task Scheduler → Task Status
- Verify computer is powered on at 9:00 AM
- Check "Wake computer to run" is enabled

### "Email not received"
- Check spam/junk folder
- Verify email_config.json settings
- Test manually: `python src/run_portfolio_analysis.py --email`

### "Authentication failed (535)"
- Regenerate App Password in Gmail
- Ensure no spaces in password
- Use App Password, not regular Gmail password

### "File not found errors"
- Verify Working Directory: `C:\workspace\portfolio_analyser`
- Check file paths in run_portfolio_analysis.py

### "Task runs but no output"
- Run manually first to verify it works
- Check Task History for error codes
- Ensure Python virtual environment is correct

---

## Maintenance

### Weekly:
- Check email inbox for daily reports (should be 7 per week Mon-Sun)
- Verify reports show current date

### Monthly:
- Review Task History for failures
- Update holdings.csv and targets.csv as needed
- Check signal_history.csv is growing (performance tracking)

### When updating code:
- No need to modify scheduled task
- Changes to notebooks/Python code take effect automatically
- Only update task if changing paths or run time

---

## Security Notes

- ✅ App Password is safer than regular password
- ✅ email_config.json is excluded from git (.gitignore)
- ✅ Never commit email credentials to GitHub
- ❌ Don't share email_config.json with anyone

**If App Password is compromised:**
1. Revoke it: https://myaccount.google.com/apppasswords
2. Generate new one
3. Update email_config.json

---

## Success Checklist

- [ ] Gmail App Password generated
- [ ] email_config.json configured
- [ ] Test email successful (manual run)
- [ ] Windows Task created (9:00 AM daily)
- [ ] Manual task run successful
- [ ] Email received with PDF + Excel
- [ ] Waited 24 hours and received automated email

**Once all checked, automation is complete!** 🎉

You'll now receive daily portfolio analysis every morning at 9:00 AM without doing anything.
