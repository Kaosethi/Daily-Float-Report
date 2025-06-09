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
import time as time_module
from datetime import datetime, timedelta, time
import pytz
import logging
# Import our custom logger
from logger_config import log_info, log_debug, log_success, log_error, log_warning, log_wait

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

def run_report():
    import pytz
    BANGKOK_TZ = pytz.timezone("Asia/Bangkok")

    log_info("Extracting V2 balance...")
    V2_balance = safe_float(login_and_test_v2())
    V2_time = datetime.now(BANGKOK_TZ) if V2_balance is not None else None
    if V2_balance is not None:
        log_success(f"Extracted V2 Balance: {V2_balance:,.2f} THB at {V2_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    log_info("Extracting VAS balance...")
    VAS_balance = safe_float(login_vas())
    VAS_time = datetime.now(BANGKOK_TZ) if VAS_balance is not None else None
    if VAS_balance is not None:
        log_success(f"Extracted VAS Balance: {VAS_balance:,.2f} THB at {VAS_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    log_info("Extracting CIMB balance...")
    CIMB_balance = safe_float(login_and_get_cimb_balance())
    CIMB_time = datetime.now(BANGKOK_TZ) if CIMB_balance is not None else None
    if CIMB_balance is not None:
        log_success(f"Extracted CIMB Balance: {CIMB_balance:,.2f} THB at {CIMB_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

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

    log_info("Report generated:")
    logging.info(report)

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
                log_error(f"Failed to send email: {e}")
        else:
            # Credentials missing, so email cannot be sent
            log_error("SendGrid credentials not set. Email not sent due to missing credentials.")
    else:
        # One or more balances are missing, so email will not be sent
        log_error("One or more balances missing. Email not sent due to incomplete data.")

    # --- Clean up downloads directory ---
    import glob
    downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
    for file_path in glob.glob(os.path.join(downloads_dir, "*")):
        try:
            os.remove(file_path)
            log_success(f"Deleted: {file_path}")
        except Exception as e:
            log_error(f"Could not delete {file_path}: {e}")

    return all_balances_ok

if __name__ == "__main__":
    # --- Restore this code for real scheduling
    # Always use Asia/Bangkok time for scheduling
    BANGKOK_TZ = pytz.timezone("Asia/Bangkok")
    log_info("Scheduler started. Waiting for next run at 2:01 Asia/Bangkok time...")
    
    last_run_date = None
    last_failed_retry_datetime = None
    retry_on_failure = False
    
    # Define the daily scheduled run time (10:00)
    SCHEDULED_RUN_HOUR = 2
    SCHEDULED_RUN_MINUTE = 1
    
    # Define retry window end time (09:00)
    RETRY_END_HOUR = 9
    RETRY_END_MINUTE = 1
    
    # Define minimum time between retries (1 hour)
    RETRY_INTERVAL = timedelta(hours=1)
    
    while True:
        now_bangkok = datetime.now(BANGKOK_TZ)
        current_date = now_bangkok.date()
        
        # Create datetime objects for comparisons
        scheduled_time = BANGKOK_TZ.localize(datetime.combine(
            current_date, 
            time(SCHEDULED_RUN_HOUR, SCHEDULED_RUN_MINUTE)
        ))
        
        retry_end_time = BANGKOK_TZ.localize(datetime.combine(
            current_date,
            time(RETRY_END_HOUR, RETRY_END_MINUTE)
        ))
        
        # Check if it's time for the daily scheduled run
        is_scheduled_run_time = (
            now_bangkok.time().hour == SCHEDULED_RUN_HOUR and
            now_bangkok.time().minute == SCHEDULED_RUN_MINUTE and
            (last_run_date is None or last_run_date != current_date)
        )
        
        # Normal daily run at 2:01
        if is_scheduled_run_time:
            log_info(f"Starting scheduled daily run at {now_bangkok.strftime('%Y-%m-%d %H:%M:%S')}")
            success = run_report()
            if success:
                last_run_date = current_date
                retry_on_failure = False
                log_success("Scheduled report completed successfully")
            else:
                retry_on_failure = True
                last_failed_retry_datetime = now_bangkok
                log_warning("Report run failed. Will retry in one hour.")

        # Handle retry logic
        elif retry_on_failure:
            # Check if we're within retry window and enough time has passed since last attempt
            time_for_retry = (
                now_bangkok.time().minute == 0 and  # Only retry on the hour
                last_failed_retry_datetime is not None and
                (now_bangkok - last_failed_retry_datetime) >= RETRY_INTERVAL
            )
            
            # Check if we're still before the retry cutoff time
            within_retry_window = now_bangkok < retry_end_time
            
            if time_for_retry and within_retry_window:
                log_info(f"Retrying extraction at {now_bangkok.strftime('%H:%M')}...")
                success = run_report()
                if success:
                    last_run_date = current_date
                    retry_on_failure = False
                    log_success("Retry attempt completed successfully")
                else:
                    last_failed_retry_datetime = now_bangkok
                    log_warning("Retry attempt failed. Will try again in one hour.")
            
            # If we've passed the retry window end time, stop retrying until next day
            elif now_bangkok >= retry_end_time:
                log_warning(f"Maximum retry window reached (after {RETRY_END_HOUR:02d}:{RETRY_END_MINUTE:02d}). Will not retry until next scheduled run.")
                retry_on_failure = False

        log_debug(f"Current time: {now_bangkok.strftime('%Y-%m-%d %H:%M:%S')} - Waiting for next check...")
        time_module.sleep(15)