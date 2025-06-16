#!/usr/bin/env python
# Quick test script to run the report immediately

import sys
from generate_report import run_report
from logger import log_step, log_info, log_success, log_error

if __name__ == "__main__":
    log_step("TESTING IMMEDIATE RUN")
    log_info("Running report immediately for testing")
    
    try:
        success = run_report()
        if success:
            log_success("Test run completed successfully")
            sys.exit(0)
        else:
            log_error("Test run failed")
            sys.exit(1)
    except Exception as e:
        log_error(f"Test run encountered an exception: {str(e)}")
        sys.exit(1)
