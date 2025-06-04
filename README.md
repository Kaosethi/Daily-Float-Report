# Daily Float Report Automation

## Overview

This project automates the process of fetching daily float balances from three banking systems (CIMB, V2, and VAS), calculating the reconciliation, and sending a formatted report via email. The script is designed to run daily at a scheduled time and includes robust error handling and retry logic for data retrieval and email sending.

## Features

-   **Automated Data Extraction**: Uses Selenium to log into banking portals and extract balance information.
-   **Balance Reconciliation**: Calculates the difference between CIMB balance and the sum of V2 and VAS balances.
-   **Email Reporting**: Sends a daily report in both plain text and HTML format using SendGrid.
-   **Single Timestamp in Email**: The email report includes only one "Report generated at: [timestamp]" line at the top, not per-balance timestamps.
-   **Console Timestamps**: Each balance extraction prints a timestamp in the console for audit/debugging, but these are not included in the email.
-   **Scheduled Execution**: Configured to run daily at 02:00 (Asia/Bangkok time) using an internal Python scheduler.
-   **Retry-on-Failure Logic**: If any balance extraction fails, the script retries the entire extraction process every hour, on the hour, from 03:00 up to and including 09:00. After 09:00, it stops retrying until the next scheduled day.
-   **Environment Variable Configuration**: Securely manages credentials and API keys using a `.env` file.
-   **Fail-Safe Mechanism**: The email is only sent if all three balances are successfully extracted; otherwise, no email is sent and retries are triggered.
-   **Automatic Cleanup**: Deletes downloaded report files from the `downloads` directory after processing.
-   **Timezone Aware**: Scheduling logic is pinned to Asia/Bangkok timezone regardless of server's system time.

## Prerequisites

-   Python 3.7+ (developed with Python 3.11+ in mind)
-   `pip` (Python package installer)
-   A `chromedriver` compatible with your installed Chrome browser version (Selenium uses this).

## Setup

1.  **Clone the repository (if applicable) or download the project files.**

2.  **Install Python dependencies:**
    Navigate to the project directory in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    Create a file named `.env` in the root of the project directory. Copy the contents of `.env.example` (if provided) or add the following variables, replacing the placeholder values with your actual credentials:

    ```env
    # V2 System Credentials
    V2_URL=your_v2_login_url
    V2_USERNAME=your_v2_username
    V2_PASSWORD=your_v2_password

    # VAS System Credentials
    VAS_URL=your_vas_login_url
    VAS_USERNAME=your_vas_username
    VAS_PASSWORD=your_vas_password
    VAS_DOWNLOAD_DIR=downloads # Relative path for downloaded VAS reports

    # CIMB System Credentials
    CIMB_URL=https://www.bizchannel.cimbthai.com/corp/common2/login.do?action=loginRequest
    CIMB_COMPANY_ID=your_cimb_company_id
    CIMB_USERNAME=your_cimb_username
    CIMB_PASSWORD=your_cimb_password

    # SendGrid API Configuration
    SENDGRID_API_KEY="your_sendgrid_api_key"
    SENDGRID_FROM_EMAIL=your_sender_email@example.com
    SENDGRID_TO_EMAIL=recipient1@example.com,recipient2@example.com # Comma-separated for multiple recipients
    ```

4.  **Ensure `chromedriver` is accessible:**
    -   Download the `chromedriver` executable that matches your Google Chrome browser version.
    -   Place it in a directory that is part of your system's PATH, or specify its path directly in the Selenium WebDriver setup within the Python scripts if modified for that purpose.

## Running the Script

### Manual Execution

To run the report generation process manually once:

1.  Open your terminal or command prompt.
2.  Navigate to the project directory.
3.  Execute the script:
    ```bash
    python generate_report.py
    ```
    (Note: The script is currently configured for scheduled execution. To run manually, you might need to temporarily modify the `if __name__ == "__main__":` block in `generate_report.py` to call `run_report()` directly and comment out the scheduling loop.)

### Scheduled Execution

The script `generate_report.py` is configured to run automatically every day at 00:15 Asia/Bangkok time.

1.  Open your terminal or command prompt.
2.  Navigate to the project directory.
3.  Start the script:
    ```bash
    python generate_report.py
    ```
4.  The script will print: `Scheduler started. Waiting for next run at 00:15 Asia/Bangkok time...` and then `Waiting for next run...` every 30 seconds.
5.  **Keep the terminal window open and the script running.** If the script is stopped or the terminal is closed, the scheduler will cease to operate.

For deployment on a server (e.g., DigitalOcean), you should use a process manager like `systemd`, `supervisor`, or `pm2` to ensure the script runs continuously and restarts on failure or server reboot.

## Error Handling

-   The script includes `try-except` blocks for web interactions and API calls to handle common errors gracefully.
-   If any of the CIMB, V2, or VAS balances cannot be retrieved, the email report will **not** be sent, and a message will be logged to the console indicating incomplete data.
-   The console output provides detailed logs of the script's operations, including successful extractions, errors, and email sending status.

## File Structure

```
Daily-Float-Report/
├── .env                  # Local environment variables (sensitive, not committed to Git)
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── generate_report.py    # Main script for orchestrating report generation and scheduling
├── main.py               # Contains the core Selenium logic for logging into bank portals and extracting data
├── README.md             # This file
├── requirements.txt      # Python package dependencies
└── downloads/            # Directory for temporary storage of downloaded reports (e.g., from VAS)
```

## Troubleshooting

-   **`NameError: name 'pytz' is not defined`**: Ensure `import pytz` is at the top of `generate_report.py`.
-   **Selenium WebDriver Errors (e.g., `WebDriverException`)**: 
    -   Verify `chromedriver` is compatible with your Chrome version.
    -   Ensure `chromedriver` is in your system's PATH or its path is correctly specified.
-   **Timezone Issues**: The script is hardcoded to use `Asia/Bangkok` for scheduling. If reports run at unexpected times, verify this setting. The server's system timezone does not affect this script's schedule.
-   **Email Not Sending**: 
    -   Check `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, and `SENDGRID_TO_EMAIL` in your `.env` file.
    -   Ensure the API key has the necessary permissions (Mail Send).
    -   Check console logs for error messages from SendGrid or messages about incomplete balance data.
-   **SSL Certificate Errors**: The script includes a patch for common SSL issues with SendGrid by setting `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` environment variables using the `certifi` package. If SSL errors persist, ensure `certifi` is installed and up-to-date.

## Future Enhancements

-   Implement a more robust process management solution for server deployment (e.g., Docker, systemd service).
-   Add more detailed logging to a file.
-   Introduce a web interface for viewing reports or triggering manual runs.
-   Expand to include more banking systems or report types.

