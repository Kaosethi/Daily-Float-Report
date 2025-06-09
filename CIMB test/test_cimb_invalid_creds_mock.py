import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main3 import login_and_get_cimb_balance
from selenium.webdriver.common.by import By

def test_cimb_invalid_creds():
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
        # Simulate login form fields
        def find_element_side_effect(by, value):
            if by == By.ID and value == "corpId":
                return company_field
            elif by == By.ID and value == "userName":
                return user_field
            elif by == By.ID and value == "passwordEncryption":
                return password_field
            elif by == By.NAME and value == "submit1":
                return login_button
            return MagicMock()
        mock_driver.find_element.side_effect = find_element_side_effect
        # Patch WebDriverWait to raise TimeoutException on dashboard load (login fails)
        wait_instance = MagicMock()
        from selenium.common.exceptions import TimeoutException
        wait_instance.until.side_effect = TimeoutException("Login failed: invalid credentials")
        MockWait.return_value = wait_instance
        # Mock frame switching (no-op)
        mock_driver.switch_to.default_content.return_value = None
        mock_driver.switch_to.frame.return_value = None
        result = login_and_get_cimb_balance()
        print(f"login_and_get_cimb_balance() result with invalid creds: {result}")
        assert result is None, "Should return None on invalid credentials!"
        print("Test passed: CIMB invalid credentials returns None and logs error.")

if __name__ == '__main__':
    test_cimb_invalid_creds()
