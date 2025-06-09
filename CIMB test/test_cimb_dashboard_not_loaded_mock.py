import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main3 import login_and_get_cimb_balance
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def test_cimb_dashboard_not_loaded():
    with patch('main3.webdriver.Chrome') as MockChrome, \
         patch('main3.WebDriverWait') as MockWait, \
         patch('main3.time.sleep'):
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Mock login form fields (all found)
        def find_element_side_effect(by, value):
            return MagicMock()
        mock_driver.find_element.side_effect = find_element_side_effect
        # Patch WebDriverWait to raise TimeoutException (dashboard never loads)
        wait_instance = MagicMock()
        wait_instance.until.side_effect = TimeoutException("Dashboard did not load")
        MockWait.return_value = wait_instance
        # Mock frame switching (no-op)
        mock_driver.switch_to.default_content.return_value = None
        mock_driver.switch_to.frame.return_value = None
        result = login_and_get_cimb_balance()
        print(f"login_and_get_cimb_balance() result when dashboard doesn't load: {result}")
        assert result is None, "Should return None if dashboard never loads!"
        print("Test passed: CIMB dashboard not loaded returns None and logs error.")

if __name__ == '__main__':
    test_cimb_dashboard_not_loaded()
