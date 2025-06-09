import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main3 import login_and_get_cimb_balance
from selenium.webdriver.common.by import By

def test_cimb_success():
    with patch('main3.webdriver.Chrome') as MockChrome, \
         patch('main3.WebDriverWait') as MockWait, \
         patch('main3.time.sleep'):
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Mock login form fields
        company_field = MagicMock()
        user_field = MagicMock()
        password_field = MagicMock()
        login_button = MagicMock()
        # First four find_element calls: login form
        def find_element_side_effect(by, value):
            if by == By.ID and value == "corpId":
                return company_field
            elif by == By.ID and value == "userName":
                return user_field
            elif by == By.ID and value == "passwordEncryption":
                return password_field
            elif by == By.NAME and value == "submit1":
                return login_button
            elif by == By.XPATH and "Account Service" in value:
                return MagicMock()  # menu_div
            elif by == By.ID and value == "subs8":
                return MagicMock()  # account_summary_link
            return MagicMock()
        mock_driver.find_element.side_effect = find_element_side_effect
        # Patch WebDriverWait to immediately succeed for both waits
        wait_instance = MagicMock()
        wait_instance.until.side_effect = [True, True]
        MockWait.return_value = wait_instance
        # After login, simulate menuFrame and mainFrame
        def find_elements_side_effect(by, value):
            if by == By.NAME and value == "menuFrame":
                return [MagicMock()]  # Simulate menuFrame present
            elif by == By.TAG_NAME and value == "a":
                # For menuFrame: links after menu expand (simulate 5 links)
                # For mainFrame: include account and balance links
                acct_number = os.getenv("CIMB_ACCOUNT_NUMBER", "7013252356")
                account_link = MagicMock()
                account_link.text = f"{acct_number} /THB   Some Company"
                account_link.get_attribute.return_value = "#"
                balance_link = MagicMock()
                balance_link.text = "7,123,456.78"
                balance_link.get_attribute.return_value = "#"
                # Fill with dummy links before and after
                return [MagicMock(), MagicMock(), account_link, balance_link, MagicMock()]
            return []
        mock_driver.find_elements.side_effect = find_elements_side_effect
        # Mock frame switching (no-op)
        mock_driver.switch_to.default_content.return_value = None
        mock_driver.switch_to.frame.return_value = None
        result = login_and_get_cimb_balance()
        print(f"login_and_get_cimb_balance() result: {result}")
        assert result == 7123456.78, "Balance extraction failed in happy path!"
        print("Test passed: CIMB happy path balance extraction.")

if __name__ == '__main__':
    test_cimb_success()
