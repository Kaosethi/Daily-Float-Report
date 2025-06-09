import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

def test_vas_screenshot_saved():
    with patch('main2.webdriver.Chrome') as MockChrome, \
         patch('main2.WebDriverWait') as MockWait, \
         patch('main2.glob.glob') as mock_glob, \
         patch('main2.time.sleep') as mock_sleep, \
         patch('main2.pd.read_excel') as mock_read_excel:
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        # Simulate table appears after wait
        wait_instance = MockWait.return_value
        wait_instance.until.return_value = True
        # Simulate table rows and download
        matching_row = MagicMock()
        matching_row.text = "UserAcccountStatReport_20250605.xlsx"
        download_icon = MagicMock()
        matching_row.find_element.return_value = download_icon
        mock_driver.find_elements.return_value = [matching_row]
        # Simulate file download completes
        mock_glob.side_effect = lambda pattern: ["downloads/UserAcccountStatReport_20250605.xlsx"]
        df = MagicMock()
        df.iloc.__getitem__.return_value = 12345.67  # Simulate valid float in B15
        mock_read_excel.return_value = df
        # Simulate screenshot
        screenshot_path = os.path.join(os.path.dirname(__file__), "vas_report_table.png")
        def save_screenshot(path):
            print(f"[MOCK] Screenshot saved: {path}")
            return True
        mock_driver.save_screenshot.side_effect = save_screenshot
        result = login_vas()
        print(f"login_vas() result with screenshot: {result!r}")

if __name__ == '__main__':
    test_vas_screenshot_saved()
