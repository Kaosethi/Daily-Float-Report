import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Import our custom logger
from logger_config import log_info, log_debug, log_success, log_error, log_warning, log_wait

# Load environment variables
load_dotenv()
CIMB_COMPANY_ID = os.getenv("CIMB_COMPANY_ID")
CIMB_USERNAME = os.getenv("CIMB_USERNAME")
CIMB_PASSWORD = os.getenv("CIMB_PASSWORD")

# Setup Chrome WebDriver (reuse logic from main2.py)
def setup_driver(download_dir=None):
    options = Options()
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    return webdriver.Chrome(options=options)

# CIMB login and balance extraction (stub - update selectors as needed)
def login_and_get_cimb_balance():
    driver = setup_driver()
    try:
        log_info("Navigating to CIMB login page...")
        driver.get("https://www.bizchannel.cimbthai.com/corp/common2/login.do?action=loginRequest")
        time.sleep(2)
        log_debug(f"Page title after loading login page: {driver.title}")
        log_debug(f"Current URL: {driver.current_url}")

        log_info("You may now manually press LOGOUT in the browser. Wait at least 10 seconds after the dashboard appears before logging out to ensure all debug info is printed.")

        # Fill in CIMB login form with explicit error handling
        try:
            company_field = driver.find_element(By.ID, "corpId")
            log_info("Found company ID field.")
        except Exception as e:
            log_error(f"Could not find company ID field (corpId): {e}")
            return
        try:
            user_field = driver.find_element(By.ID, "userName")
            log_info("Found username field.")
        except Exception as e:
            log_error(f"Could not find username field (userName): {e}")
            return
        try:
            password_field = driver.find_element(By.ID, "passwordEncryption")
            log_info("Found password field.")
        except Exception as e:
            log_error(f"Could not find password field (passwordEncryption): {e}")
            return
        try:
            login_button = driver.find_element(By.NAME, "submit1")
            log_info("Found login button.")
        except Exception as e:
            log_error(f"Could not find login button (submit1): {e}")
            return
        # Now fill and submit
        company_field.send_keys(CIMB_COMPANY_ID)
        user_field.send_keys(CIMB_USERNAME)
        password_field.send_keys(CIMB_PASSWORD)
        login_button.click()
        log_info("Login submitted, waiting for dashboard...")
        log_info("Login submitted, waiting for dashboard to load...")
        try:
            # Wait for URL to change to 'returnMain'
            WebDriverWait(driver, 60).until(
                EC.url_contains("returnMain")
            )
            log_success("URL changed to dashboard. Now waiting for frameset...")
            # Wait for menuFrame to appear
            WebDriverWait(driver, 60).until(
                lambda d: len(d.find_elements(By.NAME, "menuFrame")) > 0
            )
            log_success("Frameset loaded, proceeding to frame navigation.")
            log_wait("Dashboard loaded. Waiting 5 seconds...")
            time.sleep(5)
        except Exception:
            log_error("Dashboard did not load after login. Stopping.")
            return None

        # --- Frame switching logic ---
        cimb_balance = None
        try:
            # 1. Switch to menuFrame to click menu items
            driver.switch_to.default_content()
            driver.switch_to.frame("menuFrame")
            log_wait("Switched to menuFrame. Waiting 5 seconds...")
            time.sleep(5)
            # Click 'Account Service & Information Management'
            menu_div = driver.find_element(By.XPATH, "//div[contains(text(), 'Account Service')]")
            menu_div.click()
            log_success("Clicked 'Account Service & Information Management' menu.")
            log_wait("Clicked Account Service & Information Management. Waiting 5 seconds...")
            time.sleep(5)
            # Print all <a> links in menuFrame after expanding menu
            links = driver.find_elements(By.TAG_NAME, "a")
            log_debug("Links in menuFrame after expanding menu:")
            for idx, link in enumerate(links):
                log_debug(f"Link {idx}: '{link.text.strip()}' | href={link.get_attribute('href')}")
            # Click 'Account Summary' using its id
            account_summary_link = driver.find_element(By.ID, "subs8")
            account_summary_link.click()
            log_success("Clicked 'Account Summary' link.")
            log_wait("Clicked Account Summary. Waiting 10 seconds...")
            time.sleep(10)
        except Exception:
            log_error("Could not find or click the menu or Account Summary in menuFrame.")
        try:
            # 2. Switch to mainFrame to extract account and balance
            driver.switch_to.default_content()
            driver.switch_to.frame("mainFrame")
            log_wait("Switched to mainFrame. Printing all <a> elements for debug...")
            links = driver.find_elements(By.TAG_NAME, "a")
            for idx, link in enumerate(links):
                log_debug(f"Link {idx}: text='{link.text.strip()}', onclick='{link.get_attribute('onclick')}'")
            log_wait("Now waiting up to 60 seconds for balance element...")
            wait_start = time.time()
            acct_number = os.getenv("CIMB_ACCOUNT_NUMBER", "7013252356")
            cimb_balance = None
            error_occurred = False
            try:
                # Extraction block
                acct_idx = None
                for idx, link in enumerate(links):
                    if acct_number in link.text:
                        acct_idx = idx
                        log_info(f"Found account link at index {acct_idx}: {link.text}")
                        break
                if acct_idx is not None and acct_idx + 1 < len(links):
                    balance_link = links[acct_idx + 1]
                    balance_text = balance_link.text.strip().replace(',', '')
                    try:
                        cimb_balance = float(balance_text)
                        log_success(f"Extracted CIMB Available Balance for {acct_number}: {cimb_balance} THB")
                    except Exception as e:
                        log_error(f"Could not parse balance '{balance_text}' as float: {e}")
                        error_occurred = True
                    log_wait("Extracted balance. Waiting 5 seconds...")
                    time.sleep(5)
                else:
                    log_error(f"Could not find account {acct_number} or its balance link.")
                    error_occurred = True
            except Exception as e:
                log_error(f"Error during extraction: {e}")
                error_occurred = True
            finally:
                # Logout logic
                logout_success = False
                for frame_name in ["topFrame", None]:
                    try:
                        driver.switch_to.default_content()
                        if frame_name:
                            driver.switch_to.frame(frame_name)
                        log_info(f"[LOGOUT] Searching for logout link in {frame_name or 'default content'}...")
                        logout_link = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'action=logout') or @onclick='logout()']"))
                        )
                        logout_link.click()
                        log_success(f"Clicked logout link in {frame_name or 'default content'}.")
                        # Wait for login page to reappear (by URL or login field)
                        driver.switch_to.default_content()
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "corpId"))
                        )
                        log_success("Logout confirmed: Login page detected.")
                        logout_success = True
                        break
                    except Exception as e:
                        log_warning(f"Could not find/click logout link in {frame_name or 'default content'}: {e}")
                if not logout_success:
                    log_warning("Logout could not be confirmed. Please check your session manually.")
            if error_occurred:
                return None
        except Exception:
            log_error("Could not find or extract the account or balance in mainFrame.")
        return cimb_balance

    except Exception as e:
        log_error(f"Error during CIMB login or scraping: {e}")
    finally:
        # Do NOT close the browser automatically so user can inspect manually
        pass

if __name__ == "__main__":
    balance = login_and_get_cimb_balance()
    if balance is not None:
        log_success(f"CIMB Available Balance: {balance:,.2f} THB")
    else:
        log_error("No CIMB balance found.")
