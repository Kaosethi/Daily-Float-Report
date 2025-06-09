import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_missing_download_icon(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal login and navigation
    mock_driver.get.side_effect = lambda url: None
    # Simulate finding username, password, button, date input, search button, etc.
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    # Simulate table rows, one matches expected report
    matching_row = MagicMock()
    matching_row.text = "UserAcccountStatReport_20250605.xlsx"
    # Simulate no download icon in the row
    matching_row.find_element.side_effect = Exception("No download icon found")
    mock_driver.find_elements.return_value = [matching_row]
    mock_chrome.return_value = mock_driver

    result = login_vas()
    print(f"login_vas() result with missing download icon: {result!r}")  # Expect None

if __name__ == '__main__':
    test_missing_download_icon()
