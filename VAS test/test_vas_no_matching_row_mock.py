import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_no_matching_row(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal navigation and login
    mock_driver.get.side_effect = lambda url: None
    # Simulate finding username, password, button, date input, search button, etc.
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    # Simulate table rows for report search, but none match the expected name/date
    mock_driver.find_elements.return_value = [
        MagicMock(text="Other Report - 01/01/2022"),
        MagicMock(text="Unrelated Data - 05/06/2025")
    ]
    mock_chrome.return_value = mock_driver

    result = login_vas()
    print(f"login_vas() result with no matching row: {result!r}")  # Expect None

if __name__ == '__main__':
    test_no_matching_row()
