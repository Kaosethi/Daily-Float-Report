import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import NoSuchElementException
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_invalid_login(mock_chrome):
    mock_driver = MagicMock()
    # Simulate login page interaction, then fail to find a post-login element
    def get_side_effect(url):
        pass  # Navigating to login page
    mock_driver.get.side_effect = get_side_effect
    # Simulate login fields and button present, but after login, dashboard element is missing
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), NoSuchElementException("Invalid login")]  # username, password, button, dashboard
    mock_chrome.return_value = mock_driver

    result = login_vas()
    print(f"login_vas() result with invalid credentials: {result!r}")  # Expect None

if __name__ == '__main__':
    test_invalid_login()
