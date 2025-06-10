from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    options.add_argument("--headless")  # Enable headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# Login to V2 system
def login_and_test_v2():
    driver = setup_driver()
    try:
        print("Opening browser and navigating to login page...")
        driver.get("https://v2.ipps.co.th/agents/login")
        
        # Use WebDriverWait for login form to load
        wait = WebDriverWait(driver, 10)
        print("Waiting for login form to load...")
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        
        print("Filling in login credentials...")
        email_field.send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        print("Clicking login button...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Login')]")))  
        login_button.click()
        
        # Wait for dashboard to load - check for multiple indicators
        print("Waiting for dashboard to load...")
        try:
            # Wait for logout button or any dashboard element to confirm successful login
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Logout')]|//div[contains(@class, 'sidebar')]|//div[text()='E-Money']"))
            )
            print("✅ Dashboard loaded successfully")
        except TimeoutException:
            print("❌ Dashboard failed to load after login - timeout")
            # Print the current URL and page source for debugging
            print(f"Current URL: {driver.current_url}")
            return None

        # Get E-Money balance using multiple strategies
        print("Attempting to extract E-Money balance...")
        balance_value = None
        
        # Take a screenshot for debugging
        try:
            screenshot_path = "dashboard_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"✅ Saved dashboard screenshot to {screenshot_path}")
        except Exception as ss_error:
            print(f"❌ Failed to save screenshot: {ss_error}")
                
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
            # Strategy 3: Even more general - find all balance texts and filter
            lambda: {
                "name": "Text search",
                "finder": lambda: next(
                    (elem for elem in driver.find_elements(By.XPATH, "//div[contains(text(), 'Balance')]")
                    if "THB" in elem.text or "฿" in elem.text),
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
