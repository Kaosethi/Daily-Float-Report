import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

def test_vas_retry_skips_crdownload():
    with patch('main2.webdriver.Chrome') as MockChrome, \
         patch('main2.glob.glob') as mock_glob, \
         patch('main2.time.sleep') as mock_sleep:
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Simulate normal login, navigation, matching row, and download icon
        mock_driver.get.side_effect = lambda url: None
        mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        matching_row = MagicMock()
        matching_row.text = "UserAcccountStatReport_20250605.xlsx"
        download_icon = MagicMock()
        matching_row.find_element.return_value = download_icon
        mock_driver.find_elements.return_value = [matching_row]
        # Simulate .crdownload file present, no completed file
        def fake_glob(pattern):
            if pattern.endswith('.crdownload'):
                return ["downloads/UserAcccountStatReport_20250605.xlsx.crdownload"]
            else:
                return []
        mock_glob.side_effect = fake_glob
        result = login_vas()
        print(f"login_vas() result with persistent .crdownload: {result!r}")  # Expect None after timeout

if __name__ == '__main__':
    test_vas_retry_skips_crdownload()
