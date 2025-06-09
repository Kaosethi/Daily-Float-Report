import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_corrupt_excel(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal login, navigation, matching row, and download icon
    mock_driver.get.side_effect = lambda url: None
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    matching_row = MagicMock()
    matching_row.text = "UserAcccountStatReport_20250605.xlsx"
    download_icon = MagicMock()
    matching_row.find_element.return_value = download_icon
    mock_driver.find_elements.return_value = [matching_row]
    mock_chrome.return_value = mock_driver

    # Patch glob.glob to simulate successful download
    with patch('main2.glob.glob') as mock_glob, \
         patch('main2.time.sleep') as mock_sleep, \
         patch('main2.pd.read_excel') as mock_read_excel:
        # Simulate downloaded file present
        mock_glob.side_effect = lambda pattern: ["downloads/UserAcccountStatReport_20250605.xlsx"]
        # Simulate pandas raising an error when reading Excel
        mock_read_excel.side_effect = Exception("Corrupted Excel file")
        result = login_vas()
        print(f"login_vas() result with corrupt Excel: {result!r}")  # Expect None

if __name__ == '__main__':
    test_corrupt_excel()
