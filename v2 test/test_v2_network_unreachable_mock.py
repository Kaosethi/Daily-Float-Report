import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import WebDriverException
from main import login_and_test_v2

@patch('main.webdriver.Chrome')
def test_network_unreachable(mock_chrome):
    mock_driver = MagicMock()
    # Simulate driver.get() raising a network error
    def get_side_effect(url):
        raise WebDriverException("Network is unreachable")
    mock_driver.get.side_effect = get_side_effect
    mock_chrome.return_value = mock_driver

    result = login_and_test_v2()
    print(f"login_and_test_v2() result with network unreachable: {result!r}")  # Expect None

if __name__ == '__main__':
    test_network_unreachable()
