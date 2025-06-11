import os
import certifi
# Patch for SSL certificate errors with SendGrid
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
# If you still get SSL errors, try running this script with Python 3.10–3.12, as some newer/older versions may have SSL bugs.
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import Mail
import schedule
import time
from datetime import datetime, timedelta
import pytz

# Import logging functionality
from logger import logger, log_info, log_error, log_warning, log_success, log_step, log_function

# Import the real extraction functions
from main import login_and_test_v2
from main2 import login_vas
from main3 import login_and_get_cimb_balance

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
TO_EMAIL = [email.strip() for email in os.getenv("SENDGRID_TO_EMAIL", "").split(",") if email.strip()]

def safe_float(val):
    try:
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val)
    except Exception:
        return None

@log_function
def run_report():
    import pytz
    BANGKOK_TZ = pytz.timezone("Asia/Bangkok")
    log_step("Starting Daily Float Report Generation")
    
    log_info("Extracting V2 balance...")
    V2_balance = safe_float(login_and_test_v2())
    V2_time = datetime.now(BANGKOK_TZ) if V2_balance is not None else None
    if V2_balance is not None:
        log_success(f"Extracted V2 Balance: {V2_balance:,.2f} THB at {V2_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        log_error("Failed to extract V2 balance")

    log_info("Extracting VAS balance...")
    VAS_balance = safe_float(login_vas())
    VAS_time = datetime.now(BANGKOK_TZ) if VAS_balance is not None else None
    if VAS_balance is not None:
        log_success(f"Extracted VAS Balance: {VAS_balance:,.2f} THB at {VAS_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        log_error("Failed to extract VAS balance")

    log_info("Extracting CIMB balance...")
    CIMB_balance = safe_float(login_and_get_cimb_balance())
    CIMB_time = datetime.now(BANGKOK_TZ) if CIMB_balance is not None else None
    if CIMB_balance is not None:
        log_success(f"Extracted CIMB Balance: {CIMB_balance:,.2f} THB at {CIMB_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        log_error("Failed to extract CIMB balance")

    # Use a single report generated timestamp for the email (Asia/Bangkok time)
    report_generated_time = datetime.now(BANGKOK_TZ)
    report_generated_str = report_generated_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    report = f"""
Daily Float Reconciliation Report\nReport generated at: {report_generated_str}\n\n"""
    if CIMB_balance is not None:
        report += f"CIMB Balance: {CIMB_balance:,.2f} THB\n"
    else:
        report += f"CIMB Balance: ERROR\n"
    if V2_balance is not None:
        report += f"V2 Balance: {V2_balance:,.2f} THB\n"
    else:
        report += f"V2 Balance: ERROR\n"
    if VAS_balance is not None:
        report += f"VAS Balance: {VAS_balance:,.2f} THB\n"
    else:
        report += f"VAS Balance: ERROR\n"

    report_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    html_report = f'''
<html>
  <head>
    <style>
      body {{ font-family: Arial, sans-serif; }}
      .report-table {{ border-collapse: collapse; width: 500px; margin: 18px 0; }}
      .report-table th, .report-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
      .report-table th {{ background-color: #f2f2f2; font-weight: bold; }}
      .ok {{ color: #228B22; font-weight: bold; }}
      .warn {{ color: #B22222; font-weight: bold; }}
      .error {{ color: #B22222; font-weight: bold; }}
    </style>
  </head>
  <body>
    <h2>Daily Float Reconciliation Report for {report_date}</h2>
    <p><b>Report generated at: {report_generated_str}</b></p>
    <table class="report-table">
      <tr><th>Account</th><th>Balance (THB)</th></tr>
      <tr><td>CIMB</td><td>{(f"{CIMB_balance:,.2f}" if CIMB_balance is not None else '<span class="error">ERROR</span>')}</td></tr>
      <tr><td>V2</td><td>{(f"{V2_balance:,.2f}" if V2_balance is not None else '<span class="error">ERROR</span>')}</td></tr>
      <tr><td>VAS</td><td>{(f"{VAS_balance:,.2f}" if VAS_balance is not None else '<span class="error">ERROR</span>')}</td></tr>
    </table>
'''

    all_balances_ok = None not in (CIMB_balance, V2_balance, VAS_balance)

    if all_balances_ok:
        result = CIMB_balance - (V2_balance + VAS_balance)
        report += f"\nCIMB - (V2 + VAS) = {result:,.2f} THB\n\n"
        if result >= 0:
            summary = f"CIMB balance is sufficient. Surplus: {result:,.2f} THB."
            html_report += f'<p class="ok">CIMB - (V2 + VAS) = {result:,.2f} THB</p>'
            html_report += f'<p class="ok">CIMB balance is sufficient. Surplus: {result:,.2f} THB.</p>'
        else:
            summary = f"Warning: Combined V2 and VAS float exceeds CIMB account by {abs(result):,.2f} THB!"
            html_report += f'<p class="warn">CIMB - (V2 + VAS) = {result:,.2f} THB</p>'
            html_report += f'<p class="warn">Warning: Combined V2 and VAS float exceeds CIMB account by {abs(result):,.2f} THB!</p>'
        report += summary
    else:
        report += "\nOne or more balances could not be extracted. Please check logs.\n"
        html_report += '<p class="error">One or more balances could not be extracted. Please check logs.</p>'

    html_report += '</body></html>'

    log_info("Generated report summary:")
    for line in report.strip().split('\n'):
        log_info(line)

    # --- Send email via SendGrid ---
    # First, check if all balances were successfully retrieved
    if None not in (CIMB_balance, V2_balance, VAS_balance):
        # If all balances are present, then check for SendGrid credentials
        if SENDGRID_API_KEY and FROM_EMAIL and TO_EMAIL:
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY.strip('"'))
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=TO_EMAIL,
                subject=f"Daily Float Reconciliation Report for {report_date}",
                plain_text_content=report,
                html_content=html_report
            )
            try:
                response = sg.send(message)
                log_success(f"Email sent! Status code: {response.status_code}")
            except Exception as e:
                log_error(f"Failed to send email: {e}", exc_info=True)
        else:
            # Credentials missing, so email cannot be sent
            log_error("SendGrid credentials not set. Email not sent due to missing credentials.")
    else:
        # One or more balances are missing, so email will not be sent
        log_error("One or more balances missing. Email not sent due to incomplete data.")

    # --- Clean up downloads directory ---
    import glob
    log_info("Cleaning up downloads directory...")
    downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
    for file_path in glob.glob(os.path.join(downloads_dir, "*")):
        try:
            os.remove(file_path)
            log_success(f"Deleted: {file_path}")
        except Exception as e:
            log_error(f"Could not delete {file_path}: {e}")

    return all_balances_ok

if __name__ == "__main__":
    # Always use Asia/Bangkok time for scheduling
    BANGKOK_TZ = pytz.timezone("Asia/Bangkok")
    now_bangkok = datetime.now(BANGKOK_TZ)
    
    log_step("Scheduler started")
    log_info("Waiting for next run at 00:15 Asia/Bangkok time...")
    log_info(f"Current date/time: {now_bangkok.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize to yesterday's date so it will run today if in the correct time window
    yesterday = (now_bangkok - timedelta(days=1)).date()
    
    # If current time is after today's run window (00:15-00:16), set last_run_date to today
    # Otherwise, set to yesterday to allow today's run
    if now_bangkok.hour > 0 or (now_bangkok.hour == 0 and now_bangkok.minute >= 17):
        last_run_date = now_bangkok.date()  # Already ran today
    else:
        last_run_date = yesterday  # Allow run today
    log_info(f"Initialized last_run_date to: {last_run_date}")
    
    last_failed_retry_hour = None
    retry_on_failure = False
    while True:
        now_bangkok = datetime.now(BANGKOK_TZ)
        hour = now_bangkok.hour
        minute = now_bangkok.minute
        
        # Log current time every 5 minutes for debugging
        if minute % 5 == 0 and now_bangkok.second < 2:
            log_info(f"Scheduler check: Current time is {hour:02d}:{minute:02d}:{now_bangkok.second:02d} Bangkok time")

        # Log detailed scheduler condition info at 00:15
        if hour == 0 and 15 <= minute < 17:
            log_info(f"Scheduler condition check: hour={hour}, minute={minute}, current_date={now_bangkok.date()}, last_run_date={last_run_date}")
            
        # Normal daily run at 00:15 (allow 00:15-00:16 to ensure we don't miss it)
        if hour == 0 and 15 <= minute < 17 and last_run_date != now_bangkok.date():
            success = run_report()
            if success:
                last_run_date = now_bangkok.date()
                retry_on_failure = False
            else:
                retry_on_failure = True
                last_failed_retry_hour = hour

        # Retry on the hour if previous run failed, but only up to and including 09:00
        elif retry_on_failure and minute == 0 and last_failed_retry_hour != hour and 1 <= hour <= 9:
            log_info(f"Retrying extraction at {hour:02d}:00...")
            success = run_report()
            if success:
                last_run_date = now_bangkok.date()
                retry_on_failure = False
                log_success("Retry succeeded")
            else:
                last_failed_retry_hour = hour
                log_warning(f"Retry at {hour:02d}:00 failed, will try again next hour if within retry window")
            # If it's after 09:00, stop retrying until the next day
        elif retry_on_failure and hour > 9:
            log_warning("Maximum retry window reached (after 09:00). Will not retry until next scheduled day.")
            retry_on_failure = False

        log_info("Waiting for next run...")
        time.sleep(30)