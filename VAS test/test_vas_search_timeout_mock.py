import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from selenium.common.exceptions import TimeoutException
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_search_timeout(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal login and navigation up to search
    mock_driver.get.side_effect = lambda url: None
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    # Simulate WebDriverWait timeout when waiting for table
    with patch('main2.WebDriverWait') as mock_wait:
        instance = mock_wait.return_value
        instance.until.side_effect = TimeoutException("Table did not appear in time")
        mock_chrome.return_value = mock_driver
        result = login_vas()
        print(f"login_vas() result with search timeout: {result!r}")  # Expect None

if __name__ == '__main__':
    test_search_timeout()
