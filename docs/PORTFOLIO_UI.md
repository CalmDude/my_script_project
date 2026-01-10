# Portfolio UI - Complete User Manual

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Menu Options](#menu-options)
- [Tabs Guide](#tabs-guide)
- [Understanding Charts](#understanding-charts)
- [Daily Workflows](#daily-workflows)
- [Configuration & Settings](#configuration--settings)
- [Email Automation](#email-automation)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Start the UI
```powershell
.\scripts\start_ui.ps1
```
Open: **http://localhost:8501**

### Stop the UI
Press **Ctrl+C** in terminal or run:
```powershell
.\scripts\stop_ui.ps1
```

---

## Menu Options

**Access the menu:** Click the hamburger icon (☰) in the top-right corner

### Available Options:

1. **Rerun (R)**
   - **What it does:** Refreshes ALL data and recalculates everything
   - **When to use:** After adding trades, if prices look stale, or charts aren't updating
   - **Keyboard shortcut:** Press `R`

2. **Settings**
   - **What it does:** Opens Streamlit app settings
   - **Options:** Theme colors (light/dark mode), wide mode, run on save
   - **When to use:** Customize appearance and behavior

3. **Print**
   - **What it does:** Opens browser print dialog
   - **When to use:** Print current tab for records or offline review

4. **Record a screencast**
   - **What it does:** Records video of your interactions (Streamlit feature)
   - **When to use:** Rarely needed - mainly for demos or tutorials

5. **Developer options**
   - **What it does:** Shows technical debugging info
   - **When to use:** Troubleshooting only - can ignore for normal use

6. **Clear cache (C)**
   - **What it does:** Clears cached price data and forces fresh API calls
   - **When to use:** If prices are frozen, incorrect, or not updating
   - **Keyboard shortcut:** Press `C`
   - **⚠️ IMPORTANT:** Use this if Charts show wrong prices!

**Most Used Options:**
- **Rerun** - Daily use when you want fresh data
- **Clear cache** - When prices are stuck or wrong

---

## Tabs Guide

### 1. ➕ Buy Tab
**Purpose:** Purchase stocks and add to your portfolio

**What You See:**
- Ticker Symbol input field
- Quantity input (supports decimals for crypto)
- Purchase Price input field
- Purchase Date selector
- Notes input field (optional)
- "Get Current Price" button
- "Add Transaction" button

**How It Works:**

1. **Enter Ticker Symbol**
   - Examples: `TSLA`, `NVDA`, `BTC-USD`, `SOL-USD`
   - Automatically converts to uppercase

2. **Get Current Price (Optional)**
   - Click button to fetch live market price
   - Shows current price from Yahoo Finance
   - Use this to verify market value before buying

3. **Enter Transaction Details**
   - **Quantity:** Number of shares/coins (e.g., 10 or 0.5 for crypto)
   - **Price:** What you paid per share
   - **Date:** Transaction date (defaults to today)
   - **Notes:** Optional notes like "Buying the dip" or "Dollar cost averaging"

4. **Add Transaction**
   - Click "Add Transaction" button
   - If ticker exists: Updates average cost and total quantity
   - If new ticker: Creates new position
   - Automatically logs to `transactions.csv`

**Example Scenarios:**

**New Position:**
- Buy 10 NVDA @ $145.50
- Result: 10 shares @ $145.50 avg cost

**Adding to Existing Position:**
- You own: 5 NVDA @ $140.00
- You buy: 10 NVDA @ $148.00
- Result: 15 shares @ $145.33 avg cost (weighted average)

**Notes Examples:**
- "Buying support level S1"
- "Adding to position - FULL HOLD + ADD signal"
- "Dollar cost averaging - weekly buy"

---

### 2. ➖ Sell Tab
**Purpose:** Sell positions and track realized gains/losses

**What You See:**
- Dropdown of your active holdings
- Current position info (quantity & avg cost)
- Quantity to Sell input
- Sell Price input field
- Sell Date selector
- Notes input field (optional)
- Transaction Preview section
- "Get Current Price" button
- "Sell Stock" button

**How It Works:**

1. **Select Stock**
   - Dropdown shows only stocks you own (quantity > 0)
   - Displays current position: "10 shares @ $145.50 avg cost"

2. **Enter Sell Details**
   - **Quantity:** Cannot exceed what you own
   - **Price:** What you're selling at
   - **Date:** Transaction date
   - **Notes:** Optional notes like "Taking profits" or "Stop loss triggered"

3. **Review Transaction Preview**
   - **Cost Basis:** What you originally paid (avg cost × quantity)
   - **Proceeds:** What you'll receive (sell price × quantity)
   - **Gain/Loss:** Profit or loss in dollars and percentage
   - Updates live as you type

4. **Execute Sale**
   - Click "Sell Stock" button
   - Updates holdings (reduces quantity)
   - Logs transaction with realized P/L
   - Shows summary with remaining shares

**Transaction Preview Metrics:**
- **Cost Basis:** $1,450.00 (10 shares @ $145 avg)
- **Proceeds:** $1,600.00 (10 shares @ $160 sell price)
- **Gain/Loss:** +$150.00 (+10.34%)

**Notes Examples:**
- "Taking profits at resistance R1"
- "Rebalancing portfolio"
- "Stop loss - REDUCE signal triggered"
- "Tax loss harvesting"

---

### 3. 📈 Holdings Tab
**Purpose:** View all current positions with live prices and P/L

**What You See:**
- **Quick Stats (Top Metrics)**
  - Portfolio Value (total market value)
  - Total Cost (what you paid)
  - Total Gain/Loss (profit/loss $ and %)
  - Number of Positions

- **Holdings Table**
  - Ticker, Quantity, Avg Cost, Current Price
  - Market Value, Cost Basis, Gain/Loss ($), Gain/Loss (%)
  - Color-coded: Green for gains, Red for losses
  - Last Updated date

- **Show All Holdings** (expandable)
  - Includes zero-quantity positions (stocks you sold completely)

**How It Works:**
- Automatically fetches live prices from Yahoo Finance
- Calculates unrealized gains/losses
- Updates when you click "Rerun" or refresh page
- Prices cached briefly for performance

**Understanding the Columns:**
- **Market Value:** Current price × quantity (what it's worth now)
- **Cost Basis:** Avg cost × quantity (what you paid)
- **Gain/Loss:** Market value - cost basis
- **Gain/Loss %:** (Gain/Loss ÷ Cost Basis) × 100

**Example Row:**
```
TSLA | 72 shares | $310.60 avg | $445.01 current
Market: $32,040.72 | Cost: $22,363.20 | Gain: +$9,677.52 (+43.27%)
```

---

### 4. 📊 Charts Tab
**Purpose:** Visual analysis with interactive charts and performance tracking

**What You See:**

**Quick Stats Dashboard:**
- Portfolio Value, Total Cost, Total P/L, # Positions
- Same as Holdings tab but at top for quick reference

**Left Column Charts:**

1. **Allocation by Market Value (Pie Chart)**
   - Shows % of portfolio in each stock
   - Hover to see exact dollar amounts
   - Helps identify concentration risk

2. **Position Sizes (Horizontal Bar Chart)**
   - Market value of each position
   - Sorted from smallest to largest
   - Identify overweight/underweight positions

**Right Column Charts:**

3. **Gain/Loss by Position (Color-Coded Bars)**
   - Dollar amount of profit/loss per stock
   - Green bars = gains, Red bars = losses
   - Shows which positions are contributing most to P/L

4. **Performance % (Return % Chart)**
   - Percentage return for each position
   - Color scale: Red (losses) → Yellow (breakeven) → Green (gains)
   - **Price Details Table:** Shows Current Price, Avg Cost, Return % for verification
   - Hover over bars to see exact numbers

**Transaction History Section:**

5. **Buy vs Sell Volume (Pie Chart)**
   - Total dollar amount of buys vs sells
   - Shows if you're net buyer or seller

6. **Transaction Volume by Type (Bar Chart)**
   - Dollar volume of BUY and SELL transactions
   - Color-coded green (BUY) and red (SELL)

**Interpreting Performance %:**
- **Green bars (positive %):** Making money - price above your avg cost
- **Red bars (negative %):** Losing money - price below your avg cost
- **Longer bars:** Bigger gains or losses
- **Example:** +43% means stock doubled from your cost, -50% means lost half

**Price Details Table:**
Always check this table to verify chart accuracy:
```
Ticker | Current Price | Avg Cost | Return %
TSLA   | 445.01       | 310.60   | +43.27
BTC-USD| 90,629.57    | 50,090.10| +80.93
```

**If charts look wrong:** Click hamburger menu → Clear cache → Rerun

---

### 5. 🎯 Targets Tab
**Purpose:** Set and manage target portfolio allocations

**What You See:**
- Editable table with your target allocations
- Columns: Ticker, Target % (0-100), Target Value ($)
- "Add Row" button
- "Delete Selected Rows" button
- Validation message (shows if percentages sum to 100%)
- "Save Targets" button

**How It Works:**

1. **Edit Target Percentages**
   - Click any cell in "Target %" column
   - Type new percentage (e.g., 25 for 25%)
   - Must sum to 100% total

2. **Target Value

2. **Target Value Auto-Calculation**
   - Calculated automatically based on your total portfolio value
   - Target Value = Target % × Total Portfolio Value
   - Updates when you rerun the analysis notebook

3. **Add New Targets**
   - Click "Add Row"
   - Enter ticker and percentage
   - Save changes

4. **Remove Targets**
   - Select rows to delete
   - Click "Delete Selected Rows"
   - Confirm deletion

5. **Save Changes**
   - Click "Save Targets" button
   - Updates `data/targets.csv`
   - Used by portfolio analysis notebook for buy/sell recommendations

**Validation:**
- ✅ Green message: "Valid! Percentages sum to 100%"
- ⚠️ Yellow message: "Percentages sum to X% (should be 100%)"

**Best Practices:**
- Keep 5-10% in cash for opportunities
- Target percentages should reflect your risk tolerance
- Review and adjust quarterly
- Ensure total = 100% before saving

**Example Allocation:**
```
Ticker  | Target % | Target Value
TSLA    | 40%      | $52,671
BTC-USD | 60%      | $79,006
Total   | 100%     | $131,677
```

---

### 6. 📜 History Tab
**Purpose:** Complete transaction log with filtering and export

**What You See:**

**Summary Stats (Top Metrics):**
- Total BUY transactions count
- Total SELL transactions count
- Total Buy Volume ($)
- Total Sell Volume ($)
- Net Cash Flow (invested - withdrawn)
- Total Transactions

**Filters Section:**
1. **Transaction Type Filter**
   - All: Show both BUY and SELL
   - BUY only
   - SELL only

2. **Ticker Filter**
   - Multi-select dropdown
   - Filter by one or multiple tickers
   - "All tickers" shows everything

3. **Date Range Filter**
   - From Date (start)
   - To Date (end)
   - Filter transactions within range

**Transaction List:**
- Date & Time (when transaction occurred)
- Type (BUY or SELL, color-coded)
- Ticker symbol
- Quantity (shares/coins)
- Price (per share)
- Total Value (quantity × price)
- Notes (your custom notes + auto-generated P/L for sells)

**Features:**
- **Sortable Columns:** Click column headers to sort
- **Color Coding:** Green rows (BUY), Red rows (SELL)
- **Download CSV:** Export filtered data to Excel
- **Detailed View:** Expandable notes section for long text

**Use Cases:**
- Tax reporting (download year-end transactions)
- Performance review (see all sells with realized P/L)
- Trading journal (review your notes and decisions)
- Reconciliation (verify transaction accuracy)

**Notes Field Shows:**
- **BUY transactions:** Your custom notes (e.g., "Buying the dip")
- **SELL transactions:** Realized P/L + your notes (e.g., "Realized P/L: $150.00 (+10.34%). Taking profits at R1")

---

## Understanding Charts

### Allocation Pie Chart
**What it shows:** Percentage of total portfolio in each position
**How to read:**
- Larger slices = bigger positions
- Hover to see exact dollar amounts and percentages
- Use to identify concentration risk

**Red flags:**
- One position > 50% (too concentrated)
- Allocation doesn't match your targets

### Position Sizes Bar Chart
**What it shows:** Dollar value of each position
**How to read:**
- Longer bars = larger positions
- Sorted smallest to largest
- Compare to your target allocations

**Action items:**
- Short bars with high target % = need to buy more
- Long bars with low target % = need to reduce

### Gain/Loss Dollar Chart
**What it shows:** Unrealized profit/loss in dollars for each position
**How to read:**
- Green bars = making money
- Red bars = losing money
- Bar length = size of gain/loss

**What it means:**
- Shows which stocks are contributing most to portfolio P/L
- Use for rebalancing decisions
- Helps identify winners vs losers

### Performance % Chart
**What it shows:** Return percentage for each position
**How to read:**
- Color scale: Red (losses) → Yellow (0%) → Green (gains)
- Positive % (right side) = profitable
- Negative % (left side) = losing money
- **Check Price Details table below chart to verify accuracy**

**Example:**
- TSLA at +43.27% = Bought at $310.60, now $445.01
- BTC-USD at +80.93% = Bought at $50,090, now $90,629

**If chart shows wrong colors:**
1. Check Price Details table for actual numbers
2. Click hamburger menu → Clear cache
3. Click Rerun
4. Chart colors should fix themselves

---

## Daily Workflows

### Morning Review Routine
1. **Start UI:** `.\scripts\start_ui.ps1`
2. **Open in Browser:** http://localhost:8501
3. **Check Holdings Tab:**
   - Review overnight price changes
   - Check total P/L
   - Note any big movers
4. **Check Charts Tab:**
   - Review Performance % chart
   - Look for positions hitting targets
   - Check allocation vs targets
5. **Check Targets Tab:**
   - See which positions need rebalancing

**Time:** 2-3 minutes

### Executing a Trade (Buy)
1. **Go to Buy Tab**
2. **Enter ticker** (e.g., NVDA)
3. **Click "Get Current Price"** to see market price
4. **Enter quantity** you want to buy
5. **Enter price** you paid (or use fetched price)
6. **Add notes** (optional): "Buying support level S1"
7. **Click "Add Transaction"**
8. **Verify** success message and updated average cost
9. **Go to Holdings Tab** and click "Rerun" to see updated portfolio

**Time:** 1-2 minutes

### Executing a Trade (Sell)
1. **Go to Sell Tab**
2. **Select stock** from dropdown
3. **Review current position** displayed
4. **Click "Get Current Price"** to see market price
5. **Enter quantity** to sell
6. **Enter sell price**
7. **Review Transaction Preview** (cost basis, proceeds, P/L)
8. **Add notes** (optional): "Taking profits at resistance"
9. **Click "Sell Stock"**
10. **Verify** P/L summary and remaining shares
11. **Go to History Tab** to see transaction logged

**Time:** 2-3 minutes

### Weekly Portfolio Review
1. **Holdings Tab:** Review all positions and total P/L
2. **Charts Tab:**
   - Check allocation pie chart (are you balanced?)
   - Review Performance % (which stocks are winners/losers?)
   - Look at transaction volume (am I overtrading?)
3. **History Tab:**
   - Filter by date range (last 7 days)
   - Review all trades and notes
   - Export CSV for records
4. **Targets Tab:**
   - Adjust targets if strategy changed
   - Check if rebalancing needed

**Time:** 10-15 minutes

### End of Month
1. **History Tab:**
   - Filter date range: First to last day of month
   - Review all transactions
   - Download CSV for tax records
2. **Calculate monthly return:**
   - Note beginning of month portfolio value
   - Note end of month portfolio value
   - Calculate % change
3. **Review notes** from trades
   - What worked? What didn't?
   - Learn from wins and losses

---

## Configuration & Settings

### Streamlit Config File
**Location:** `.streamlit/config.toml`

```toml
[server]
headless = true

[browser]
gatherUsageStats = false
```

**Settings Explained:**
- `headless = true`: Doesn't auto-open external browser (good for VS Code workflow)
- `gatherUsageStats = false`: Disables telemetry - no usage data sent to Streamlit servers

### Data Files

**All files located in:** `data/` folder

1. **holdings.csv**
   - **Purpose:** Current stock positions
   - **Updated by:** Buy Tab, Sell Tab
   - **Read by:** All tabs, portfolio analysis notebook
   - **Columns:** ticker, quantity, avg_cost, last_updated, min_quantity

2. **targets.csv**
   - **Purpose:** Target portfolio allocations
   - **Updated by:** Targets Tab
   - **Read by:** Portfolio analysis notebook (for buy/sell recommendations)
   - **Columns:** ticker, target_pct, target_value

3. **transactions.csv** *(NEW - Auto-created on first transaction)*
   - **Purpose:** Complete transaction history log
   - **Updated by:** Buy Tab, Sell Tab (automatically)
   - **Read by:** History Tab, Charts Tab
   - **Columns:** date, type, ticker, quantity, price, total_value, notes
   - **Used for:** Historical analysis, tax reporting, performance tracking

**Data Integrity:**
- All tools read/write same CSV files
- No conflicts between UI and notebooks
- Data syncs automatically
- Always use UI or notebooks, never edit CSVs directly (unless you know what you're doing)

---

## Email Automation

**Get daily portfolio reports delivered to your inbox automatically at 9:00 AM!**

### Overview
Set up Windows Task Scheduler to run portfolio analysis every morning and email you the results (PDF + Excel).

### Prerequisites
- Gmail account
- 15 minutes for setup
- Windows Task Scheduler

---

### Step 1: Gmail App Password Setup (5 minutes)

**Why App Password?**  
More secure than your regular Gmail password, can be revoked independently.

**Setup Process:**

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow prompts to enable (if not already on)

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Windows Computer"
   - Click "Generate"
   - **Copy the 16-character password** (shown once only!)

3. **Configure Email Settings**
   - Edit `config/email_config.json`:
   ```json
   {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "sender_email": "your-email@gmail.com",
     "sender_password": "xxxx xxxx xxxx xxxx",  ← Paste App Password here
     "recipient_email": "your-email@gmail.com",
     "subject_prefix": "Portfolio Analysis"
   }
   ```

---

### Step 2: Test Email (2 minutes)

**Run test command:**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Test email sending
python src/run_portfolio_analysis.py --email
```

**Expected Output:**
```
[OK] Email sent successfully to your-email@gmail.com
```

**What You'll Receive:**
- **Subject:** Portfolio Analysis - 2026-01-10 14:30
- **Attachments:** 
  - trading_playbook_YYYYMMDD_HHMMSS.pdf
  - portfolio_tracker_YYYYMMDD_HHMMSS.xlsx
- **Body:** Summary of holdings, buy/sell signals, key metrics

**If Errors:**
- `Authentication failed`: Check App Password (no spaces, 16 chars)
- `SMTP connection error`: Firewall blocking port 587
- `File not found`: Verify email_config.json exists in config/

---

### Step 3: Windows Task Scheduler (10 minutes)

**Option A: Automated Script (Recommended)**

```powershell
.\scripts\setup_automation.ps1
```

Creates scheduled task that runs daily at 9:00 AM.

**Option B: Manual Setup**

1. **Open Task Scheduler:**
   - Press `Win + R`, type: `taskschd.msc`, press Enter

2. **Create New Task:**
   - Click "Create Task" (not "Create Basic Task")
   - **General Tab:**
     - Name: `Portfolio Analyser - Daily Report`
     - Description: `Run portfolio analysis and email results`
     - ☑ Run whether user is logged on or not
     - ☑ Run with highest privileges

3. **Triggers Tab:**
   - Click "New..."
   - Begin the task: "On a schedule"
   - Settings: "Daily"
   - Start: Today's date, **9:00:00 AM**
   - Recur every: 1 days
   - ☑ Enabled
   - Click "OK"

4. **Actions Tab:**
   - Click "New..."
   - Action: "Start a program"
   - **Program/script:** `C:\workspace\portfolio_analyser\.venv\Scripts\python.exe`
   - **Arguments:** `src/run_portfolio_analysis.py --email`
   - **Start in:** `C:\workspace\portfolio_analyser`
   - Click "OK"

5. **Conditions Tab:**
   - ☑ Start only if computer is on AC power
   - ☑ Wake the computer to run this task
   - ☐ Stop if computer switches to battery power

6. **Settings Tab:**
   - ☑ Allow task to be run on demand
   - ☑ Run task as soon as possible after scheduled start is missed
   - ☐ Stop the task if it runs longer than: 3 hours
   - Click "OK"

7. **Save:**
   - Enter your Windows password when prompted

---

### Step 4: Test the Scheduled Task (2 minutes)

**Manual Test Run:**
1. Open Task Scheduler (`taskschd.msc`)
2. Find: `Portfolio Analyser - Daily Report`
3. Right-click → **"Run"**
4. Watch Status: "Running" → "Ready"
5. **Check email** (arrives in 1-2 minutes)

**View Task History:**
- Right-click task → Properties → History tab
- Look for "Task Started" and "Task Completed" events
- **Last Run Result:** 0x0 = success

---

### Customization

**Change Run Time:**
- Edit Triggers tab in task properties
- Popular times:
  - 6:00 AM (before work)
  - 4:00 PM (market close)
  - 9:00 PM (evening review)

**Weekdays Only:**
- Change "Daily" to "Weekly"
- Select Mon-Fri only

**Multiple Recipients:**
```json
"recipient_email": "you@gmail.com, spouse@gmail.com"
```

**Custom Subject Line:**
```json
"subject_prefix": "📊 Daily Portfolio Update"
```

---

### Troubleshooting Email Automation

**Email Not Received:**
- Check spam/junk folder
- Verify email_config.json settings
- Test manually first

**Task Not Running:**
- Check Task Scheduler → Task Status
- Verify "Wake computer" is enabled
- Ensure computer is on at scheduled time

**Authentication Failed (535):**
- Regenerate App Password
- Ensure no spaces in password
- Use App Password, not regular Gmail password

**Task Runs But No Output:**
- Run manually first to verify
- Check Task History for error codes
- Verify Python paths are correct

---

### Security Notes
- ✅ App Password is safer than regular password
- ✅ email_config.json excluded from git (.gitignore)
- ✅ Never commit credentials to GitHub
- ❌ Don't share email_config.json

**If App Password Compromised:**
1. Revoke: https://myaccount.google.com/apppasswords
2. Generate new one
3. Update email_config.json

---

## Advanced Features

These features run automatically when you execute `portfolio_analysis.ipynb`.

### 1. Data Sanity Checks

**Location:** Notebook Cell 4

**What It Does:**
- Validates price data (no $0 or negative prices)
- Checks data freshness (not stale/cached)
- Flags >20% overnight moves (possible errors)
- Confirms valid API responses

**Output:**
- `[ERROR]` = Critical issues - don't trade until fixed
- `[WARN]` = Review before trading
- `[OK]` = All clear

**When To Act:**
- **Price = $0:** API issue or delisted stock - remove from holdings
- **Stale data:** Weekend/holiday - wait for market open
- **Large move:** Verify on Yahoo/Google Finance

---

### 2. Signal Performance Tracker

**Location:** Notebook Cell 15

**What It Does:**
- Automatically logs every "FULL HOLD + ADD" signal
- Tracks entry price when signal triggers
- Calculates returns 30/60/90 days later
- Shows win rates and average returns

**Data File:** `data/signal_history.csv` (auto-created)

**Timeline:**
- **Days 1-29:** Collecting data, no stats yet
- **Day 30:** First 30-day performance results appear
- **Day 60:** 60-day statistics available
- **Day 90:** Full historical performance data

**Sample Output:**
```
30-DAY PERFORMANCE:
  Win rate: 65.0% (13/20 wins)
  Avg return: +8.2%
  Median: +6.5%
  Best: +45.3%
  Worst: -12.1%
```

**Purpose:**
- Build confidence in the system over time
- Identify which quality ratings perform best
- Validate Larsson methodology for your style
- Track improvement as you refine entry timing

**Filters:**
- Only tracks EXCELLENT, GOOD, OK quality signals
- Excludes EXTENDED and WEAK signals
- Automatically deduplicates (won't log same ticker twice same day)

---

### 3. Signal Change Tracking

**Location:** Notebook Cell 8

**What It Does:**
- Compares today's signals to previous trading day
- Highlights new buy opportunities
- Identifies new defensive signals
- Shows price changes for active positions

**Output Sections:**

1. **Signal Changes** - Which stocks changed signals
2. **New Buy Opportunities** - FULL HOLD + ADD signals that just appeared
3. **New Defensive Signals** - Stocks that turned bearish
4. **Price Changes** - Active positions that moved >1%

**Use Cases:**
- Focus on what's NEW instead of reviewing everything
- Catch buy opportunities as they emerge
- Get alerted to positions needing defensive action

---

## VS Code Workflow

---

## Troubleshooting

### Keep Everything in VS Code

**Step 1:** Start in terminal
```powershell
.\scripts\start_ui.ps1
```

**Step 2:** Open Simple Browser
- Press `Ctrl+Shift+P`
- Type "Simple Browser: Show"
- Enter: `http://localhost:8501`

**Step 3:** Split view
- Drag Simple Browser tab to right side
- Code on left, UI on right

**Why this works:**
- Config prevents external browser opening
- Everything stays in one window
- Easy to make code changes and test
- No context switching

**Pro tip:** Pin the Simple Browser tab so it doesn't close accidentally

---

## Troubleshooting

### Prices Not Loading / Wrong Prices

**Symptoms:**
- Charts show wrong colors (profitable stocks showing red)
- Prices seem old or frozen
- "Current Price" shows $0.00

**Solutions:**
1. **Clear cache:** Hamburger menu → Clear cache (C)
2. **Rerun:** Hamburger menu → Rerun (R)
3. **Check internet:** Verify network connection
4. **Verify ticker:** Some tickers may not exist on Yahoo Finance
5. **Check Price Details table:** Under Performance % chart, verify actual prices fetched

**If still wrong:**
- Close UI (Ctrl+C in terminal)
- Run: `.\scripts\stop_ui.ps1`
- Delete: `__pycache__` folders in src/
- Restart: `.\scripts\start_ui.ps1`

### Port Already in Use

**Symptom:** Error "Port 8501 is already in use"

**Solution:**
```powershell
.\scripts\stop_ui.ps1
```

Then restart:
```powershell
.\scripts\start_ui.ps1
```

### UI Won't Start

**Symptom:** Script fails, error about missing modules

**Solution:**
Check virtual environment and install dependencies:
```powershell
.\.venv\Scripts\Activate.ps1
pip install streamlit plotly pandas yfinance
```

### Charts Not Showing

**Symptoms:**
- Blank chart areas
- Error messages about plotly

**Solution:**
```powershell
pip install --upgrade plotly
```

Then restart UI.

### Transaction Not Saving

**Symptoms:**
- Click "Add Transaction" but nothing happens
- Error message appears

**Solutions:**
1. Check all required fields are filled
2. Verify quantity > 0
3. Verify price > 0
4. Check that `data/` folder exists
5. Check CSV file permissions (not read-only)

### Data Files Corrupted

**Symptoms:**
- Error loading CSV files
- Holdings/targets show weird data

**Solution:**
1. **Backup first:** Copy `data/` folder
2. **Check CSV format:** Open in text editor, verify headers
3. **Restore from backup** if available
4. **Recreate manually** if needed:

**holdings.csv:**
```csv
ticker,quantity,avg_cost,last_updated,min_quantity
TSLA,72,310.60,2026-01-04,0
BTC-USD,0.5,50090.10,2026-01-04,0.5
```

**targets.csv:**
```csv
ticker,target_pct,target_value
TSLA,0.4,52671
BTC-USD,0.6,79006
```

### Performance Degradation

**Symptoms:**
- UI slow to load
- Price fetching takes forever

**Solutions:**
1. **Reduce positions:** More stocks = more API calls
2. **Check internet speed:** Yahoo Finance may be slow
3. **Clear browser cache:** Browser settings
4. **Restart UI:** Fresh start often helps

---

## Privacy & Security

### What Stays Local
✅ **All portfolio data:** Holdings, targets, transactions  
✅ **Your notes:** Never leave your computer  
✅ **Transaction history:** Stored locally only  
✅ **Personal information:** Not collected or transmitted  

### What Goes Online
⚠️ **Yahoo Finance API:** Only ticker symbols sent (when fetching prices)  
⚠️ **Streamlit Telemetry:** Disabled via config (no usage stats sent)  

### Best Practices
- ✅ Don't expose port 8501 to internet (use localhost only)
- ✅ Don't commit sensitive CSV data to public repos
- ✅ Keep `.env` files private
- ✅ Use strong passwords if exposing to network
- ✅ Backup `data/` folder regularly

---

## Recent Updates

### v2.1 (2026-01-10)
- ✅ Added custom **notes fields** to Buy and Sell tabs
- ✅ Improved price fetching with **5-day fallback** and error handling
- ✅ Fixed **Performance % chart colors** (midpoint at 0%)
- ✅ Added **Price Details table** under Performance % chart for verification
- ✅ Enhanced error messages when price fetching fails
- ✅ Better hover tooltips on charts (shows current price, avg cost, return %)

### v2.0 (2026-01-09)
- ✅ Added Sell Stocks feature with realized P/L tracking
- ✅ Transaction history logging to transactions.csv
- ✅ Interactive charts with Plotly (pie, bar, scatter)
- ✅ Transaction history viewer with filters
- ✅ Quick stats dashboard
- ✅ Enhanced sidebar with active positions
- ✅ Reorganized tabs: Buy, Sell, Holdings, Charts, Targets, History

### v1.0 (2026-01-09)
**Location:** `.streamlit/config.toml`

```toml
[server]
headless = true

[browser]
gatherUsageStats = false
```

**Settings Explained:**
- `headless = true`: Doesn't auto-open external browser (good for VS Code workflow)
- `gatherUsageStats = false`: Disables telemetry - no usage data sent to Streamlit servers

## Data Files

### holdings.csv
**Current stock positions**
- Updated when you buy or sell stocks
- Columns: ticker, quantity, avg_cost, last_updated, min_quantity

### targets.csv
**Target portfolio allocations**
- Set your desired portfolio balance
- Columns: ticker, target_pct, target_value

### transactions.csv (NEW)
**Complete transaction history log**
- Every buy/sell is automatically logged
- Columns: date, type, ticker, quantity, price, total_value, notes
- Used for historical analysis and charts

## VS Code Workflow

### Keep Everything in VS Code

**Step 1:** Start in terminal
```powershell
.\scripts\start_ui.ps1
```

**Step 2:** Open Simple Browser
- Press `Ctrl+Shift+P`
- Type "Simple Browser: Show"
- Enter: `http://localhost:8501`

**Step 3:** Split view
- Drag Simple Browser tab to right side
- Code on left, UI on right

**Why this works:**
- Config prevents external browser opening
- Everything stays in one window
- Easy to make code changes

## Daily Usage

### Morning Routine
1. Open VS Code
2. Run `.\scripts\start_ui.ps1`
3. Open Simple Browser to localhost:8501
4. Minimize terminal

### During Trading
**Buy a Stock:**
1. Go to Buy tab
2. Enter ticker, quantity, price
3. Click "Add Transaction"
4. Holdings automatically updated

**Sell a Stock:**
1. Go to Sell tab
2. Select stock from dropdown
3. Enter quantity and sell price
4. Review gain/loss preview
5. Click "Sell Stock"
6. Realized P/L tracked in history

### End of Day
- Review performance in Charts tab
- Check allocation vs targets
- Export transaction history if needed
- Press Ctrl+C to stop UI

## Helper Scripts

### start_ui.ps1
Starts the Portfolio UI with checks:
- Verifies virtual environment exists
- Auto-installs Streamlit if missing
- Starts server with helpful messages

### v1.0 (2026-01-09)
- Initial release
- Buy stocks functionality
- Holdings viewer with live prices
- Target allocation editor
- Portfolio summary
- Helper scripts (start, stop, check)

---

## Tips & Best Practices

### Transaction Notes Best Practices
📝 **Good notes help you learn and improve:**
- "Buying S1 support - FULL HOLD + ADD signal"
- "Taking profits at R1 resistance - up 45%"
- "Rebalancing - position over target allocation"
- "Stop loss triggered - respecting risk management"
- "Dollar cost averaging - weekly $500 investment"

❌ **Avoid vague notes:**
- "Buy" (why?)
- "Trade" (what was the reasoning?)
- Leaving blank (you'll forget why you traded)

### Price Fetching Tips
- **First fetch may be slow:** Network latency normal
- **Use "Get Current Price":** Verify market price before trading
- **Check Price Details table:** Always verify what price was fetched
- **Clear cache if stuck:** Hamburger menu → Clear cache
- **Manual entry okay:** If API fails, enter price manually from your broker

### Portfolio Management Tips
- **Review Holdings weekly:** Stay on top of P/L
- **Update targets quarterly:** Markets and strategies change
- **Export History monthly:** Backup for tax season
- **Use notes religiously:** Future you will thank you
- **Rerun after trades:** See updated portfolio immediately

### Data Hygiene
- **Backup `data/` folder weekly:** Use `scripts/backup_full.ps1`
- **Don't edit CSVs manually:** Use UI or notebooks only
- **Keep transactions.csv clean:** Don't delete or modify past entries
- **Verify after trades:** Check Holdings tab shows correct new position

---

## Integration with Portfolio Analysis

### Workflow: UI → Analysis → Trading

**1. Manage Positions (Portfolio UI)**
- Track current holdings
- Log all buy/sell transactions
- Set target allocations

**2. Run Analysis (Jupyter Notebook)**
```powershell
# Run portfolio analysis
jupyter notebook notebooks/portfolio_analysis.ipynb
```
- Generates Excel tracker with buy/sell recommendations
- Creates PDF playbook with trade setups
- Analyzes technical levels and signals

**3. Execute Trades (Portfolio UI)**
- Follow recommendations from analysis
- Use notes to reference analysis: "Buying S1 from 2026-01-10 analysis"
- Log trades immediately
- Track realized P/L automatically

**4. Review Performance (Both)**
- UI: See current P/L and allocation
- Notebook: Track signal performance over 30/60/90 days
- History: Review past trades and outcomes

### Data Flow
```
Portfolio UI (transactions) → transactions.csv
                              ↓
Portfolio Analysis Notebook reads transactions.csv
                              ↓
Generates Excel Trade Log tab (auto-populated)
                              ↓
You review and execute trades
                              ↓
Log trades back in Portfolio UI
```

**Key Integration Points:**
- **Holdings.csv:** Shared by UI and analysis
- **Targets.csv:** Set in UI, used by analysis for recommendations
- **Transactions.csv:** Logged by UI, read by Excel Trade Log
- **No conflicts:** All tools work together seamlessly

---

## Quick Reference Card

### Common Actions

| Task | Steps |
|------|-------|
| **Start UI** | `.\scripts\start_ui.ps1` |
| **Stop UI** | Ctrl+C or `.\scripts\stop_ui.ps1` |
| **Refresh data** | Hamburger menu → Rerun (R) |
| **Fix stuck prices** | Hamburger menu → Clear cache (C) |
| **Buy stock** | Buy tab → Enter details → Add Transaction |
| **Sell stock** | Sell tab → Select stock → Enter details → Sell Stock |
| **Check P/L** | Holdings tab → See Total Gain/Loss |
| **View charts** | Charts tab → Review performance and allocation |
| **Set targets** | Targets tab → Edit percentages → Save Targets |
| **Review history** | History tab → Apply filters → Download CSV |
| **Verify prices** | Charts tab → Scroll to Price Details table |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **R** | Rerun (refresh all data) |
| **C** | Clear cache (force fresh prices) |
| **Ctrl+C** | Stop UI (in terminal) |

### When Things Go Wrong

| Problem | Solution |
|---------|----------|
| Wrong prices | Clear cache → Rerun |
| Charts wrong colors | Clear cache → Rerun |
| Port in use | `.\scripts\stop_ui.ps1` |
| UI won't start | Check virtual env and packages |
| Transaction won't save | Check all fields filled |
| Slow performance | Reduce positions or restart UI |

---

## Support & Help

### Where to Get Help
1. **Read this manual** - Most answers are here
2. **Check error messages** - UI shows helpful error text
3. **Review terminal output** - Debugging info appears in console
4. **Verify data files** - Check CSV format and permissions
5. **Test with clean data** - Try with minimal holdings to isolate issues

### Common Error Messages

**"Failed to fetch [TICKER] price"**
- Internet connection issue or invalid ticker
- Try again or enter price manually

**"Cannot sell more than you own"**
- Check current position quantity
- Reduce sell quantity

**"Percentages should sum to 100%"**
- In Targets tab, total must equal 100%
- Adjust percentages and save again

**"Port 8501 already in use"**
- UI already running or zombie process
- Run `.\scripts\stop_ui.ps1`

### Debug Mode
Enable detailed logging:
1. Open `src/portfolio_ui.py`
2. Find `get_current_price()` function
3. Uncomment debug line: `st.write(f"DEBUG {ticker}: ${latest_price:.2f} from {latest_date.date()}")`
4. Restart UI
5. See exactly what prices are being fetched

---

## Glossary

**Terms Used in UI:**

- **Avg Cost:** Average price paid per share (weighted average of all purchases)
- **Cost Basis:** Total amount paid for a position (avg cost × quantity)
- **Current Price:** Latest market price from Yahoo Finance
- **Gain/Loss:** Profit or loss (market value - cost basis)
- **Market Value:** Current worth of position (current price × quantity)
- **Proceeds:** Money received from selling (sell price × quantity)
- **Realized P/L:** Profit/loss from completed sale (locked in)
- **Target %:** Desired allocation percentage for this stock
- **Target Value:** Dollar amount to reach target allocation
- **Transaction:** Any buy or sell trade
- **Unrealized P/L:** Profit/loss on current positions (not sold yet)

**Chart Terms:**

- **Allocation:** How portfolio is divided among stocks (%)
- **Performance %:** Return on investment (ROI) per position
- **Position Size:** Dollar value of each holding
- **Return %:** Same as Performance % - percent gain/loss

---

## Final Notes

The Portfolio Manager UI is designed to work alongside the portfolio analysis notebook. Use the UI for daily trading activities and the notebook for deeper technical analysis and signal tracking.

**Key Philosophy:**
- **Simple:** Easy daily trade logging
- **Accurate:** Precise P/L tracking
- **Integrated:** Works with analysis tools
- **Private:** All data stays on your machine
- **Auditable:** Complete transaction history

**Remember:**
- Log every trade immediately (don't forget!)
- Use notes to capture your thinking
- Review performance regularly
- Backup your data folder
- Clear cache if prices look wrong

Happy trading! 📊🚀

---

*Last updated: January 10, 2026 - v2.1*
