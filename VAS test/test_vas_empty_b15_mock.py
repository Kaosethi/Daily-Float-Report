import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas
import pandas as pd

@patch('main2.webdriver.Chrome')
def test_empty_b15(mock_chrome):
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

    # Patch glob.glob and pd.read_excel to simulate empty B15
    with patch('main2.glob.glob') as mock_glob, \
         patch('main2.time.sleep') as mock_sleep, \
         patch('main2.pd.read_excel') as mock_read_excel:
        mock_glob.side_effect = lambda pattern: ["downloads/UserAcccountStatReport_20250605.xlsx"]
        # Simulate DataFrame with empty B15
        df = pd.DataFrame([[None if (i == 14 and j == 1) else 123 for j in range(5)] for i in range(20)])
        mock_read_excel.return_value = df
        result = login_vas()
        print(f"login_vas() result with empty B15: {result!r}")  # Expect None

if __name__ == '__main__':
    test_empty_b15()
