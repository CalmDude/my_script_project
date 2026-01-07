# Interactive Viewer & Web UI

This project includes an interactive Jupyter Notebook and a small Streamlit web app to view batch results.

Notebook
- File: `view_results.ipynb` (open in Jupyter Lab or Notebook)
- Run:
  - pip install -r requirements.txt
  - jupyter lab
- The notebook provides widgets to filter tickers, view per-symbol data, and plot SMA/VPVR charts.

Streamlit app
- File: `app.py`
- Run:
  - pip install -r requirements.txt
  - streamlit run app.py
- The app reads `batch_results.csv` and per-symbol CSVs in `./results/` and provides an interactive UI.

Notes
- If you add or modify `stocks.txt`, re-run the batch script to refresh `batch_results.csv` and per-symbol CSVs.
- Avoid committing generated CSV results to the repo unless you want them tracked (they can be large/noisy). Consider adding them to `.gitignore` if needed.
