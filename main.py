from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import os
import re
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
USERNAME = os.getenv("V2_USERNAME")
PASSWORD = os.getenv("V2_PASSWORD")

# Setup Chrome WebDriver
def setup_driver():
    options = Options()
    
    # For cloud environments, you can temporarily disable headless mode for debugging
    # Uncomment the line below in cloud and comment out the headless line if needed
    options.add_argument("--headless")  # Enable headless mode
    
    # Basic settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Mimic real browser
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    
    # More realistic user agents (rotate through these options)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]
    import random
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # Add headers to appear more legitimate
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    
    # Create and return the driver
    driver = webdriver.Chrome(options=options)
    
    # Set an implicit wait to help with element discovery
    driver.implicitly_wait(10)
    
    # Execute stealth JS to further avoid detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("window.navigator.chrome = {runtime: {}}")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    
    return driver

# Login to V2 system
def login_and_test_v2():
    driver = setup_driver()
    try:
        print("Opening browser and navigating to login page...")
        driver.get("https://v2.ipps.co.th/agents/login")
        
        # Use WebDriverWait for login form to load
        wait = WebDriverWait(driver, 15)  # Increased timeout
        print("Waiting for login form to load...")
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        
        # Add a short delay before starting to type (like a human)
        time.sleep(1.5)
        
        print("Filling in login credentials...")
        # Type like a human - character by character with random delays
        for char in USERNAME:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))  # Random delay between keystrokes
            
        # Tab to password field like a human would
        email_field.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        # Type password with human-like timing
        password_field = driver.switch_to.active_element
        for char in PASSWORD:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            
        # Short pause before clicking login (like a human would)
        time.sleep(1)

        print("Clicking login button...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Login')]")))
            
        # Hover before clicking (more human-like)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
        time.sleep(0.7)
            
        # Click the button
        login_button.click()
        
        # Check for SweetAlert errors after login attempt
        time.sleep(2)  # Short delay to allow alerts to appear
        try:
            # Check for SweetAlert dialogs which often indicate errors
            sweet_alerts = driver.find_elements(By.CLASS_NAME, "swal2-popup")
            if sweet_alerts:
                for alert in sweet_alerts:
                    alert_text = alert.text
                    print(f"⚠️ SweetAlert detected: {alert_text}")
                    # If it's a common authentication error or bot detection error, print it
                    if any(keyword in alert_text.lower() for keyword in 
                           ["invalid", "incorrect", "failed", "error", "bot", "captcha", "automated"]):
                        print(f"❌ Login error detected: {alert_text}")
            
            # Check for other visible error messages
            error_messages = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert')]")
            for error in error_messages:
                if error.is_displayed() and error.text.strip():
                    print(f"❌ Error message found: {error.text}")
        except Exception as e:
            print(f"Error checking for alerts: {e}")
            # Continue anyway
        
        # Wait for dashboard to load - check for multiple indicators with longer timeout
        print("Waiting for dashboard to load...")
        
        # Increase timeout for cloud environments
        long_wait = WebDriverWait(driver, 30)  # 30 seconds timeout
        dashboard_loaded = False
        
        # Print current URL for debugging
        print(f"Current URL after login attempt: {driver.current_url}")
        
        # Try multiple strategies to detect dashboard
        dashboard_indicators = [
            {"type": "url", "desc": "URL contains 'dashboard'", "check": lambda: "dashboard" in driver.current_url.lower()},
            {"type": "element", "desc": "Logout link present", "check": lambda: len(driver.find_elements(By.XPATH, "//a[contains(., 'Logout')]|//a[contains(@href, 'logout')]|//button[contains(., 'Logout')]")) > 0},
            {"type": "element", "desc": "Sidebar present", "check": lambda: len(driver.find_elements(By.XPATH, "//div[contains(@class, 'sidebar')]|//aside|//nav")) > 0},
            {"type": "element", "desc": "E-Money text present", "check": lambda: len(driver.find_elements(By.XPATH, "//div[contains(text(), 'E-Money')]")) > 0},
            {"type": "general", "desc": "Not on login page", "check": lambda: "login" not in driver.current_url.lower() and len(driver.find_elements(By.ID, "email")) == 0}
        ]
        
        # Check all dashboard indicators
        for indicator in dashboard_indicators:
            try:
                if indicator["check"]():
                    print(f"✅ Dashboard detected via {indicator['desc']}")
                    dashboard_loaded = True
                    break
            except Exception as e:
                print(f"Could not check {indicator['desc']}: {e}")
        
        # If no indicators were found, try waiting for any of them
        if not dashboard_loaded:
            try:
                print("No immediate dashboard indicators found. Waiting up to 30 seconds for any to appear...")
                # Try to wait for any dashboard element
                long_wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Logout')]|//div[contains(@class, 'sidebar')]|//div[contains(text(), 'E-Money')]|//div[contains(text(), 'Balance')]")))                
                print("✅ Dashboard eventually loaded after waiting")
                dashboard_loaded = True
            except TimeoutException:
                print("❌ Dashboard failed to load after extended wait")
        
        if not dashboard_loaded:
            print("❌ Could not verify dashboard loaded. Page source preview:")
            # Print a sample of the page source for debugging
            page_source = driver.page_source
            print(page_source[:500] + "... [truncated]")
            
            # Try to continue anyway - maybe we're on the dashboard but couldn't detect it
            print("Attempting to continue despite dashboard detection failure...")
        else:
            print("Dashboard successfully detected, proceeding to extract balance")

        # Get E-Money balance using multiple strategies
        print("Attempting to extract E-Money balance...")
        balance_value = None
        
        # Screenshot functionality removed as requested
                
        # Print page structure for debugging
        print("\nDumping page structure for debugging:")
        try:
            elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'E-Money')]|//div[contains(text(), 'Balance')]")
            print(f"Found {len(elements)} relevant elements:")
            for i, elem in enumerate(elements[:10]):  # Limit to first 10 for brevity
                print(f"  Element {i}: '{elem.text}', tag={elem.tag_name}, class={elem.get_attribute('class')}")
        except Exception as e:
            print(f"❌ Error dumping page structure: {e}")
        
        # Multiple extraction strategies
        strategies = [
            # Strategy 1: Original XPath (more specific)
            lambda: {
                "name": "Original XPath",
                "finder": lambda: driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'd-flex') and .//div[text()='E-Money']]//div[contains(text(), 'Balance:')]"
                )
            },
            # Strategy 2: More general XPath
            lambda: {
                "name": "General XPath",
                "finder": lambda: driver.find_element(
                    By.XPATH,
                    "//div[contains(text(), 'E-Money')]/following::div[contains(text(), 'Balance')]"
                )
            },
            # Strategy 3: Any Balance text with THB
            lambda: {
                "name": "Text search",
                "finder": lambda: next(
                    (elem for elem in driver.find_elements(By.XPATH, "//div[contains(text(), 'Balance')]")
                    if "THB" in elem.text or "฿" in elem.text),
                    None
                )
            },
            # Strategy 4: Any element with both numbers and currency indicator
            lambda: {
                "name": "Number + Currency",
                "finder": lambda: next(
                    (elem for elem in driver.find_elements(By.XPATH, "//*[contains(text(), 'THB') or contains(text(), '฿')]")
                    if re.search(r'\d', elem.text)),
                    None
                )
            },
            # Strategy 5: Extremely general - any numerical value on the page
            lambda: {
                "name": "Any Number",
                "finder": lambda: next(
                    (elem for elem in driver.find_elements(By.XPATH, "//*") 
                    if re.search(r'[\d,]+\.?\d+', elem.text) and len(elem.text) < 50),  # not too long text
                    None
                )
            }
        ]
        
        for strategy_fn in strategies:
            strategy = strategy_fn()
            try:
                print(f"Trying {strategy['name']} strategy...")
                balance_element = strategy['finder']()
                
                if balance_element:
                    text = balance_element.text.strip()
                    print(f"Found text: '{text}'")
                    
                    # Extract number using regex pattern for any number with possible decimal point
                    matches = re.findall(r'[\d,]+\.?\d*', text)
                    if matches:
                        # Take the first match and clean it
                        balance_str = matches[0].replace(',', '')
                        balance_value = float(balance_str)
                        print(f"✅ Extracted E-Money Balance: {balance_value} THB using {strategy['name']}")
                        return balance_value
                    else:
                        print(f"❌ Could not extract number from '{text}'")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"❌ {strategy['name']} failed: {e.__class__.__name__}")
            except Exception as e:
                print(f"❌ Unexpected error with {strategy['name']}: {e}")
                
        print("All extraction strategies failed")
        return None

    except Exception as e:
        print("❌ Error during login or scraping:", e)
        return None
    finally:
        driver.quit()

# Run the test
if __name__ == "__main__":
    login_and_test_v2()
