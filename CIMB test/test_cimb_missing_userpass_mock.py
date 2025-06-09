import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main3 import login_and_get_cimb_balance
from selenium.webdriver.common.by import By

def test_cimb_missing_userpass():
    with patch('main3.webdriver.Chrome') as MockChrome, \
         patch('main3.time.sleep'):
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Simulate missing username and password fields
        def find_element_side_effect(by, value):
            if by == By.ID and value == "corpId":
                return MagicMock()
            elif by == By.ID and value == "userName":
                raise Exception("No such element: userName")
            elif by == By.ID and value == "passwordEncryption":
                raise Exception("No such element: passwordEncryption")
            elif by == By.NAME and value == "submit1":
                return MagicMock()
            return MagicMock()
        mock_driver.find_element.side_effect = find_element_side_effect
        # Mock frame switching (no-op)
        mock_driver.switch_to.default_content.return_value = None
        mock_driver.switch_to.frame.return_value = None
        result = login_and_get_cimb_balance()
        print(f"login_and_get_cimb_balance() result with missing user/pass: {result}")
        assert result is None, "Should return None if username or password field is missing!"
        print("Test passed: CIMB missing username/password returns None and logs error.")

if __name__ == '__main__':
    test_cimb_missing_userpass()
