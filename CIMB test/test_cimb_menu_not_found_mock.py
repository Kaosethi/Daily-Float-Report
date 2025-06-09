import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main3 import login_and_get_cimb_balance
from selenium.webdriver.common.by import By

def test_cimb_menu_not_found():
    with patch('main3.webdriver.Chrome') as MockChrome, \
         patch('main3.WebDriverWait') as MockWait, \
         patch('main3.time.sleep'):
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Mock login form fields (all found)
        def find_element_side_effect(by, value):
            if by == By.ID and value == "corpId":
                return MagicMock()
            elif by == By.ID and value == "userName":
                return MagicMock()
            elif by == By.ID and value == "passwordEncryption":
                return MagicMock()
            elif by == By.NAME and value == "submit1":
                return MagicMock()
            elif by == By.XPATH and "Account Service" in value:
                raise Exception("Menu div not found")
            return MagicMock()
        mock_driver.find_element.side_effect = find_element_side_effect
        # Patch WebDriverWait to immediately succeed for both waits
        wait_instance = MagicMock()
        wait_instance.until.side_effect = [True, True]
        MockWait.return_value = wait_instance
        # Simulate menuFrame present
        def find_elements_side_effect(by, value):
            if by == By.NAME and value == "menuFrame":
                return [MagicMock()]
            return []
        mock_driver.find_elements.side_effect = find_elements_side_effect
        # Mock frame switching (no-op)
        mock_driver.switch_to.default_content.return_value = None
        mock_driver.switch_to.frame.return_value = None
        result = login_and_get_cimb_balance()
        print(f"login_and_get_cimb_balance() result when menu not found: {result}")
        assert result is None, "Should return None if menu div not found!"
        print("Test passed: CIMB menu not found returns None and logs error.")

if __name__ == '__main__':
    test_cimb_menu_not_found()
