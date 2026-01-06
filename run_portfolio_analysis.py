"""
Automated Portfolio Analysis Runner

Executes portfolio_analysis_v2.ipynb and generates reports.
Can be run manually or scheduled via Windows Task Scheduler.
"""

import sys
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json

def send_email_report(pdf_path, config_path):
    """Send PDF report via email"""

    # Load email configuration
    if not config_path.exists():
        print(f"⚠ Email config not found: {config_path}")
        print("  Skipping email delivery. Create email_config.json to enable.")
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Validate config
        required = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_email']
        if not all(key in config for key in required):
            print(f"⚠ Invalid email config. Required fields: {', '.join(required)}")
            return False

        print("\nSending email report...")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['sender_email']
        msg['To'] = config['recipient_email']
        msg['Subject'] = f"Portfolio Analysis - {datetime.now().strftime('%Y-%m-%d')}"

        # Email body
        body = f"""
Portfolio Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please find attached the latest Trading Playbook PDF.

This is an automated report. Do not reply to this email.
        """
        msg.attach(MIMEText(body, 'plain'))

        # Attach PDF
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_path.name)
            msg.attach(pdf_attachment)

        # Send email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)

        print(f"✓ Email sent to {config['recipient_email']}")
        return True

    except Exception as e:
        print(f"✗ Email failed: {str(e)}")
        return False

def run_portfolio_analysis():
    """Execute the portfolio analysis notebook"""

    # Setup paths
    notebook_path = Path(__file__).parent / 'portfolio_analysis_v2.ipynb'
    email_config_path = Path(__file__).parent / 'email_config.json'
    results_dir = Path(__file__).parent / 'portfolio_results'

    if not notebook_path.exists():
        print(f"ERROR: Notebook not found at {notebook_path}")
        return False

    print(f"{'='*80}")
    print(f"Portfolio Analysis Automation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    try:
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Configure executor
        ep = ExecutePreprocessor(
            timeout=600,  # 10 minutes max per cell
            kernel_name='python3',
            allow_errors=False
        )

        # Execute notebook
        print("Executing notebook cells...\n")
        ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})

        # Get timestamp for finding generated reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        print(f"\n{'='*80}")
        print(f"✅ SUCCESS - Portfolio analysis completed")
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Find the generated PDF
        timestamp_pattern = timestamp  # Use same timestamp from notebook execution
        pdf_files = list(results_dir.glob(f'trading_playbook_{timestamp_pattern}*.pdf'))

        if pdf_files:
            pdf_path = pdf_files[0]
            print(f"PDF report: {pdf_path.name}")

            # Send email if configured
            send_email_report(pdf_path, email_config_path)
        else:
            print("⚠ PDF not found - email not sent")

        print(f"{'='*80}")

        return True

    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ ERROR - Portfolio analysis failed")
        print(f"Error: {str(e)}")
        print(f"{'='*80}")
        return False

if __name__ == '__main__':
    success = run_portfolio_analysis()
    sys.exit(0 if success else 1)
