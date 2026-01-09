# Portfolio UI - User Guide

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

## Features Overview

### 1. Buy Tab (➕)
**Purchase stocks and add to portfolio**

- Enter ticker symbol (e.g., NVDA, TSLA, BTC-USD)
- Specify quantity and purchase price
- Click "Get Current Price" to fetch live market data
- Automatically calculates new average cost for existing positions
- Logs transaction to history

**Example:**
- Buy 10 NVDA @ $145.50
- If you already own 5 @ $140, new average: 15 shares @ $143.50

### 2. Sell Tab (➖)
**Sell positions and track realized gains/losses**

- Select from dropdown of current holdings
- Shows your current position before selling
- Cannot sell more than you own
- Calculates realized gain/loss automatically
- Displays cost basis, proceeds, and P/L percentage
- Logs transaction with realized gain/loss notes

**Transaction Preview:**
- Cost Basis: Original purchase price × quantity
- Proceeds: Sell price × quantity  
- Gain/Loss: Proceeds - Cost Basis

### 3. Holdings Tab (📈)
**View current portfolio positions**

- Fetches live prices from Yahoo Finance
- Displays all active positions (quantity > 0)
- Summary metrics:
  - Total Portfolio Value
  - Total Cost Basis
  - Total Gain/Loss ($ and %)
  - Number of Positions
- Color-coded gains (green) and losses (red)
- Expandable section to view zero positions

### 4. Charts Tab (📊)
**Interactive visualizations and quick stats**

**Quick Stats Section:**
- Portfolio Value, Total Cost, Total P/L, Position Count

**Visualizations:**
- **Allocation Pie Chart**: Current portfolio allocation by market value
- **Position Bar Chart**: Market value of each position (horizontal bars)
- **Gain/Loss Chart**: Unrealized gains/losses by position (color-coded)
- **Performance Chart**: Return percentage by position
- **Transaction History**: Pie chart of BUY vs SELL transactions
- **Transaction Volume**: Bar chart showing dollar volume by type
- **Activity Timeline**: Scatter plot of recent transactions

### 5. Targets Tab (🎯)
**Set and edit target allocations**

- Edit target percentages directly in table
- Add or remove rows dynamically
- Validation: Shows if percentages sum to 100%
- Target value can be set in dollars
- Click "Save Targets" to update `data/targets.csv`

### 6. History Tab (📜)
**Complete transaction history viewer**

**Summary Stats:**
- Total buys/sells count
- Total buy/sell dollar volume
- Net cash flow (invested vs withdrawn)
- Total transaction count

**Filters:**
- Filter by Type: BUY, SELL, or both
- Filter by Ticker: Multi-select from your stocks
- Date Range: Custom date filtering

**Features:**
- Sortable transaction list
- Color-coded transaction types (green=BUY, red=SELL)
- Download as CSV export
- Detailed view with notes for each transaction
- Shows quantity, price, total value, timestamp

## Configuration

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

### stop_ui.ps1
Stops all Streamlit processes:
- Finds running Streamlit instances
- Terminates them forcefully
- Frees up port 8501

### check_ui.ps1
Checks if UI is running:
- Shows process details (PID, memory)
- Tests port 8501 accessibility
- Displays access URL if running

## Integration

### With Existing Tools
The Portfolio UI uses the same CSV files as your other tools:

```
data/holdings.csv  ←  Portfolio UI reads/writes
                   ←  Jupyter notebooks read
                   ←  Analysis scripts read

data/targets.csv   ←  Portfolio UI reads/writes
                   ←  Portfolio reports read

data/transactions.csv  ←  Portfolio UI writes
                      ←  Future analysis tools read
```

**No conflicts** - all tools work together seamlessly

## Privacy & Security

### What Stays Local
- All portfolio data (holdings, targets, transactions)
- Stored in CSV files on your computer
- Never uploaded anywhere

### What Goes Online
- **Yahoo Finance API**: Only ticker symbols (when fetching prices)
- **Streamlit Telemetry**: Disabled via config

### Best Practices
- Don't expose port 8501 to internet
- Keep `.env` files private
- Don't commit sensitive CSV data to public repos
- Use localhost only (not network URL)

## Tips & Tricks

### Performance
- First price fetch may be slow (network request)
- Subsequent updates are cached briefly
- Click "Refresh Data" in sidebar to force reload

### Transaction Notes
- Sell transactions automatically include realized P/L in notes
- Use this for tax reporting and performance tracking

### Data Export
- Download transaction history as CSV from History tab
- Import into Excel for custom analysis
- Format is standard CSV - works with all tools

### Troubleshooting

**Port Already in Use:**
```powershell
.\scripts\stop_ui.ps1
```

**UI Won't Start:**
Check virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
pip install streamlit plotly
```

**Prices Not Loading:**
- Check internet connection
- Some tickers may not be on Yahoo Finance
- Enter price manually if needed

**Charts Not Showing:**
- Ensure plotly is installed: `pip install plotly`
- Check browser console for errors
- Try refreshing the page

## Version History

**v2.0** (2026-01-09)
- ✅ Added Sell Stocks feature with realized P/L tracking
- ✅ Transaction history logging to transactions.csv
- ✅ Interactive charts with Plotly (pie, bar, scatter)
- ✅ Transaction history viewer with filters
- ✅ Quick stats dashboard
- ✅ Enhanced sidebar with active positions
- ✅ Reorganized tabs: Buy, Sell, Holdings, Charts, Targets, History

**v1.0** (2026-01-09)
- Initial release
- Buy stocks functionality
- Holdings viewer with live prices
- Target allocation editor
- Portfolio summary
- Helper scripts (start, stop, check)

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in UI
3. Check terminal output for debugging
4. Ensure all dependencies installed
5. Verify data files exist and are readable
