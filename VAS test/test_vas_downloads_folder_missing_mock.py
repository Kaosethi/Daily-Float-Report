import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_downloads_folder_missing(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal login and navigation
    mock_driver.get.side_effect = lambda url: None
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    matching_row = MagicMock()
    matching_row.text = "UserAcccountStatReport_20250605.xlsx"
    download_icon = MagicMock()
    matching_row.find_element.return_value = download_icon
    mock_driver.find_elements.return_value = [matching_row]
    mock_chrome.return_value = mock_driver

    # Patch os.makedirs to ensure folder is (re)created without error
    with patch('main2.os.makedirs') as mock_makedirs, \
         patch('main2.glob.glob') as mock_glob, \
         patch('main2.time.sleep') as mock_sleep, \
         patch('main2.pd.read_excel') as mock_read_excel:
        # Simulate folder missing at first, then created
        mock_makedirs.side_effect = lambda path, exist_ok: print(f"[MOCK] os.makedirs called for: {path}")
        mock_glob.side_effect = lambda pattern: ["downloads/UserAcccountStatReport_20250605.xlsx"]
        df = MagicMock()
        df.iloc.__getitem__.return_value = 12345.67  # Simulate valid float in B15
        mock_read_excel.return_value = df
        result = login_vas()
        print(f"login_vas() result with downloads folder missing: {result!r}")  # Expect float value

if __name__ == '__main__':
    test_downloads_folder_missing()
