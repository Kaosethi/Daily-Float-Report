import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main import login_and_test_v2

@patch('main.webdriver.Chrome')
def test_login_redirect(mock_chrome):
    mock_driver = MagicMock()
    # Simulate driver.get() and driver.current_url to a wrong URL after login
    def get_side_effect(url):
        mock_driver.current_url = "https://unexpected-redirect.example.com/login"
    mock_driver.get.side_effect = get_side_effect
    # Allow all other calls
    mock_chrome.return_value = mock_driver

    result = login_and_test_v2()
    print(f"login_and_test_v2() result with unexpected login redirect: {result!r}")  # Expect None

if __name__ == '__main__':
    test_login_redirect()
