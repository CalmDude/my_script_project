# New Trading Features - Quick Reference

## 1. Data Sanity Checks ✅

**Location:** `portfolio_analysis.ipynb` - Cells 3-4

**What it does:**
- Validates price data (no $0 or negative prices)
- Checks data freshness (not stale cache)
- Flags >20% overnight moves (possible errors)
- Confirms valid API responses

**When to run:** After loading data (Cell 2)

**What to look for:**
- `[ERROR]` = Critical issues, don't trade until fixed
- `[WARN]` = Review before trading
- `[OK]` = All clear, safe to proceed

---

## 2. Signal Performance Tracker ✅

**Location:** `portfolio_analysis.ipynb` - Cells 14-15

**What it does:**
- Automatically logs every "FULL HOLD + ADD" signal
- Tracks price at signal trigger
- Calculates returns 30/60/90 days later
- Shows win rates and average returns

**Data file:** `data/signal_history.csv` (created automatically)

**Timeline:**
- Day 1-29: Collecting data
- Day 30: First 30-day results appear
- Day 60: 60-day stats available
- Day 90: Full performance history

**What you'll see:**
```
30-DAY PERFORMANCE:
  Win rate: 65.0% (13/20 wins)
  Avg return: +8.2%
  Best: +45.3%
  Worst: -12.1%
```

**Uses:**
- Build confidence in system over time
- Identify which quality signals perform best
- Track if Larsson methodology works for your style

---

## 3. Email Automation ✅

**Setup script:** `scripts/setup_automation.ps1`

**Files created:**
- `config/email_config.json` - Email settings template
- `docs/AUTOMATION_SETUP.md` - Complete setup guide

**Quick Setup (15 minutes):**

1. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate password
   - Copy 16-character code

2. **Configure Email:**
   ```powershell
   # Edit config/email_config.json
   {
     "sender_email": "your-email@gmail.com",
     "sender_password": "xxxx xxxx xxxx xxxx",  <-- paste App Password
     "recipient_email": "your-email@gmail.com"
   }
   ```

3. **Test Email:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python src/run_portfolio_analysis.py --email
   ```

4. **Create Scheduled Task:**
   ```powershell
   .\scripts\setup_automation.ps1
   ```

**Result:** 
Every day at 9:00 AM, you receive an email with:
- PDF Trading Playbook
- Excel Tracker
- Summary of signals

**No manual work required** - just check your inbox each morning!

---

## Combined Workflow

### Daily Routine (Automated):
1. **9:00 AM** - Windows Task Scheduler runs analysis
2. **9:02 AM** - Email arrives with reports
3. **You review** - Check for new signals, defensive actions

### Manual Check (When Needed):
1. Open `portfolio_analysis.ipynb`
2. Run All Cells
3. Review sanity checks (any errors?)
4. Check 5-Second Dashboard (any actions?)
5. Review "What Changed Today" (new opportunities?)
6. Check signal performance (building confidence)

### Weekly:
- Run `full_scanner.ipynb` for new S&P 500 / NASDAQ opportunities
- Review signal performance trends

### Monthly:
- Check 90-day win rates in performance tracker
- Adjust targets.csv if portfolio strategy changes
- Review defensive actions taken

---

## Files Reference

### New Files:
- `src/signal_tracker.py` - Performance tracking module
- `config/email_config.json` - Email settings
- `docs/AUTOMATION_SETUP.md` - Detailed setup guide
- `data/signal_history.csv` - Signal performance database (auto-created)

### Modified Files:
- `portfolio_analysis.ipynb` - Added 4 new cells (sanity checks, performance tracker)
- `scripts/setup_automation.ps1` - Enhanced with email support

### Data Files (Auto-Generated):
- `data/signal_history.csv` - Tracks all signals and their outcomes
- `portfolio_results/*.xlsx` - Daily Excel trackers
- `portfolio_results/*.pdf` - Daily PDF playbooks

---

## Troubleshooting

### Sanity Checks showing errors?
- **Price = $0**: API issue or delisted stock, remove from holdings
- **Stale data**: Weekend/holiday, wait for market open
- **Large overnight move**: Verify with finance site (Yahoo/Google Finance)

### Performance Tracker not showing stats?
- **Day 1-29**: Says "[WAIT] Need 30 days" - Normal, keep running
- **After 30 days still empty**: Check `data/signal_history.csv` exists
- **No signals logged**: Only logs "FULL HOLD + ADD" signals

### Email not working?
- **Authentication failed**: Wrong App Password, regenerate
- **SMTP error**: Firewall blocking port 587
- **No email received**: Check spam folder, verify config

### Scheduled task not running?
- Open Task Scheduler (`taskschd.msc`)
- Find: "Portfolio Analysis - Daily Report"
- Check Last Run Result (0x0 = success)
- View History tab for errors

---

## What's Next?

These 3 features are now active:

✅ **Data Sanity Checks** - Catch bad data before trading
✅ **Signal Performance Tracker** - Build confidence over 90 days
✅ **Email Automation** - Receive daily reports automatically

**To activate automation:**
1. Follow `docs/AUTOMATION_SETUP.md` (15 minutes)
2. Test manually once
3. Wait for tomorrow's 9:00 AM email

**To start tracking performance:**
1. Just run `portfolio_analysis.ipynb` daily
2. Signals logged automatically
3. Stats appear after 30 days

**No code changes needed** - everything works automatically!

---

## Support

- **Setup questions:** See `docs/AUTOMATION_SETUP.md`
- **Performance tracking:** See `src/signal_tracker.py` docstrings
- **Data validation:** See cells 3-4 in `portfolio_analysis.ipynb`

All three features are **trader-focused** - designed to help you trade better, not code better!
