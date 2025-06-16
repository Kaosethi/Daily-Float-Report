from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
import pandas as pd  # For parsing Excel
import glob  # For finding downloaded files

# Import logging functionality
from logger import logger, log_info, log_error, log_warning, log_success, log_step, log_function

# Load environment variables
load_dotenv()
VAS_USERNAME = os.getenv("VAS_USERNAME")
VAS_PASSWORD = os.getenv("VAS_PASSWORD")

# Setup Chrome WebDriver with custom download directory
@log_function
def setup_driver(download_dir=None):
    log_info("Setting up Chrome WebDriver")
    options = Options()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set up Chrome preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False
    }
    if download_dir:
        prefs["download.default_directory"] = os.path.abspath(download_dir)
        prefs["download.prompt_for_download"] = False
        prefs["directory_upgrade"] = True
        prefs["safebrowsing.enabled"] = True
    options.add_experimental_option("prefs", prefs)

    # Optional: disable the popup warning UI entirely
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")

    return webdriver.Chrome(options=options)

# Login to VAS and select previous day's report and download/parse report
@log_function
def login_vas():
    log_step("VAS Login and Report Download")
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    driver = setup_driver(download_dir=download_dir)
    try:
        log_info("Navigating to VAS login...")
        driver.get("https://va-vasbo.ipps.co.th/vas-web/auth/login")
        time.sleep(2)

        log_info("Entering login credentials...")
        driver.find_element(By.ID, "usernameforshow").send_keys(VAS_USERNAME)
        driver.find_element(By.ID, "passwordforshow").send_keys(VAS_PASSWORD)
        driver.find_element(By.ID, "buttonforshow").click()
        time.sleep(3)

        log_info("Redirecting to report page...")
        driver.get("https://va-vasbo.ipps.co.th/vas-web/report/amc_all_report/")
        log_info("Waiting for page to load completely...")
        time.sleep(5)  # Increased wait time

        # Select previous day's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        log_info(f"Selecting report date: {yesterday}")

        try:
            # Try multiple methods to find the date input field
            date_input = None
            selectors = [
                (By.ID, "businessDate"),
                (By.NAME, "businessDate"),
                (By.XPATH, "//input[contains(@id, 'Date') or contains(@name, 'Date')]"),
                (By.XPATH, "//input[@type='date' or @type='text'][contains(@placeholder, 'date') or contains(@class, 'date')]"),
                (By.CSS_SELECTOR, "input.form-control[type='text']")
            ]
            
            # Try each selector
            for method, selector in selectors:
                try:
                    log_info(f"Trying to find date input with {method}: {selector}")
                    date_input = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((method, selector))
                    )
                    log_success(f"Found date input with {method}: {selector}")
                    break
                except:
                    continue
            
            if date_input is None:
                # Last resort: take screenshot and find all input elements
                driver.save_screenshot("vas_report_page.png")
                log_warning("Could not find date input field by standard selectors. Listing all inputs:")
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for i, inp in enumerate(inputs):
                    try:
                        log_info(f"Input {i}: id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, type={inp.get_attribute('type')}")
                    except:
                        pass
                # Try the first text input as fallback
                text_inputs = [inp for inp in inputs if inp.get_attribute('type') == 'text']
                if text_inputs:
                    date_input = text_inputs[0]
                    log_warning("Using first text input as fallback for date")
            
            # If we found a date input, use it
            if date_input:
                driver.execute_script(f"arguments[0].value = '{yesterday}'", date_input)
            else:
                raise Exception("Could not find date input field using any method")
        except Exception as e:
            log_error(f"Error finding date input: {str(e)}")
            raise

        # Click Search - try multiple methods to find the search button
        log_info("Looking for Search button...")
        
        # Take screenshot for debugging
        driver.save_screenshot("vas_before_search.png")
        log_success("Saved screenshot before search attempt")
        
        search_button = None
        search_selectors = [
            (By.XPATH, "//button[contains(text(), 'Search')]"),
            (By.XPATH, "//input[@type='submit' and (contains(@value, 'Search') or contains(@value, 'search'))]"),
            (By.XPATH, "//button[contains(@class, 'search') or contains(@id, 'search')]"),
            (By.CSS_SELECTOR, "button.btn-search, button.search-btn"),
            (By.XPATH, "//button[contains(@onclick, 'search')]"),
            (By.XPATH, "//a[contains(text(), 'Search')]"),
            (By.XPATH, "//span[contains(text(), 'Search')]/parent::button"),
            (By.XPATH, "//i[contains(@class, 'search')]/parent::button")
        ]
        
        # Try each selector
        for method, selector in search_selectors:
            try:
                log_info(f"Trying to find search button with {method}: {selector}")
                search_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((method, selector))
                )
                log_success(f"Found search button with {method}: {selector}")
                break
            except:
                continue
        
        if search_button is None:
            # Last resort: list all buttons and clickable elements
            log_warning("Could not find search button by standard selectors. Listing all buttons:")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                try:
                    btn_text = btn.text.strip()
                    btn_class = btn.get_attribute("class")
                    log_info(f"Button {i}: text='{btn_text}', class='{btn_class}'")
                    # If the button has search-related text, use it
                    if "search" in btn_text.lower():
                        search_button = btn
                        log_warning(f"Using button with text: {btn_text}")
                        break
                except:
                    pass
            
            # If still not found, try other clickable elements
            if search_button is None:
                clickable_elements = driver.find_elements(By.XPATH, "//a | //input[@type='submit'] | //input[@type='button']")
                for i, elem in enumerate(clickable_elements):
                    try:
                        elem_text = elem.text.strip() if elem.tag_name == "a" else elem.get_attribute("value")
                        log_info(f"{elem.tag_name.capitalize()} {i}: text/value='{elem_text}'")
                        if "search" in (elem_text or "").lower():
                            search_button = elem
                            log_warning(f"Using {elem.tag_name} with text: {elem_text}")
                            break
                    except:
                        pass
                
                # Last resort - try the first button that looks like it might be a submit
                if search_button is None and buttons:
                    for btn in buttons:
                        try:
                            btn_class = (btn.get_attribute("class") or "").lower()
                            if "primary" in btn_class or "submit" in btn_class or "search" in btn_class:
                                search_button = btn
                                log_warning(f"Using first button with relevant class: {btn_class}")
                                break
                        except:
                            pass
                    
                    # If still no luck, just use the first button
                    if search_button is None and buttons:
                        search_button = buttons[0]
                        log_warning("Using first button as last resort")
        
        if search_button:
            search_button.click()
            log_success("Search action triggered")
        else:
            log_error("Could not find any search button or clickable element")
            raise Exception("No search button found")
            
        # Save another screenshot after clicking search
        time.sleep(1)
        driver.save_screenshot("vas_after_search.png")
        log_info("Saved screenshot after search attempt")

        # Wait for the result to appear with more flexible selectors
        log_info("Waiting for report results to appear...")
        try:
            # Try multiple selectors for detecting results
            result_selectors = [
                (By.XPATH, "//td[contains(text(), '.csv') or contains(text(), 'Report')]"),
                (By.XPATH, "//table//tr[position() > 1]"),  # Any table row beyond header
                (By.XPATH, "//div[contains(@class, 'result') or contains(@id, 'result')]"),
                (By.XPATH, "//div[contains(@class, 'table')]"),
                (By.XPATH, "//a[contains(@href, '.csv') or contains(@href, '.xlsx')]"),
            ]
            
            # Try each selector
            found = False
            for method, selector in result_selectors:
                try:
                    log_info(f"Looking for results with {method}: {selector}")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((method, selector))
                    )
                    log_success(f"Found results with {method}: {selector}")
                    found = True
                    break
                except:
                    continue
                    
            if not found:
                log_warning("Could not detect results with standard selectors, but proceeding anyway")
                    
        except Exception as e:
            log_warning(f"Warning: Could not confirm results appeared: {str(e)} - attempting to proceed anyway")
            
        # Take screenshot of results page
        driver.save_screenshot("vas_search_results.png")
        log_success("Report results page captured (next step: download).")
        time.sleep(2)  # Additional wait to ensure page is fully loaded

        # Step 1: Build expected filename
        file_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        expected_filename = f"UserAcccountStatReport_{file_date}.xlsx"

        # Step 2: Find all rows in the report table
        rows = driver.find_elements(By.XPATH, "//table//tr")

        # DEBUG: Log all table row texts
        log_info("DEBUG: Table rows found:")
        for idx, row in enumerate(rows[:10]):
            log_info(f"Row {idx}: {row.text}")
        # Save screenshot for visual debug
        driver.save_screenshot('vas_report_table.png')
        log_info("Saved screenshot: vas_report_table.png")

        downloaded = False
        # Relaxed matching: look for report prefix and date
        file_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        for row in rows:
            try:
                if ("UserAcccountStatReport" in row.text and file_date in row.text):
                    log_success(f"Found row with report (partial match): {row.text}")
                    # Find the download icon and click it, wait until clickable
                    download_icon = row.find_element(By.XPATH, ".//i[contains(@class, 'fa-file-o')]")
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ".//i[contains(@class, 'fa-file-o')]")))
                    download_icon.click()
                    downloaded = True
                    log_info("Downloading report...")
                    break
            except Exception as e:
                continue
        # Only print and return error if NO row was found
        if not downloaded:
            log_error(f"Could not find report row for {expected_filename}")
            driver.quit()
            return None

        # Step 3: Wait for the file to finish downloading
        downloaded_file_path = os.path.join(download_dir, expected_filename)
        timeout = 30  # seconds
        waited = 0
        while waited < timeout:
            # Check if file exists and is not a .crdownload
            if os.path.exists(downloaded_file_path) and not any(glob.glob(downloaded_file_path + ".crdownload")):
                log_success(f"Download complete: {downloaded_file_path}")
                break
            time.sleep(1)
            waited += 1
        else:
            log_error(f"Download timed out for {expected_filename}")
            driver.quit()
            return None

        # Step 4: Parse Excel file to extract value from cell B15
        try:
            df = pd.read_excel(downloaded_file_path, header=None)  # Read without headers for fixed cell
            value = df.iloc[14, 1]  # Row 15 (index 14), Column B (index 1)
            log_success(f"Extracted VAS Balance: {value} THB")
            return value
        except Exception as e:
            log_error(f"Error parsing Excel file: {e}", exc_info=True)
            return None

    finally:
        driver.quit()

# Run
if __name__ == "__main__":
    log_step("Starting VAS report extraction process")
    balance = login_vas()
    if balance is not None:
        log_success(f"VAS extraction complete: {balance} THB")
    else:
        log_error("VAS extraction failed to get balance")
