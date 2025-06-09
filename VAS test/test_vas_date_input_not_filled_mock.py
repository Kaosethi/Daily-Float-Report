import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import login_vas

@patch('main2.webdriver.Chrome')
def test_date_input_not_filled(mock_chrome):
    mock_driver = MagicMock()
    # Simulate normal login and navigation
    mock_driver.get.side_effect = lambda url: None
    # Simulate finding username, password, button, date input, search button, etc.
    # But the date input is not filled correctly (simulate empty value)
    date_input = MagicMock()
    date_input.get_attribute.return_value = ''  # Date input remains empty
    mock_driver.find_element.side_effect = [MagicMock(), MagicMock(), MagicMock(), date_input, MagicMock(), MagicMock()]
    # Simulate no results after search due to missing date
    mock_driver.find_elements.return_value = []
    mock_chrome.return_value = mock_driver

    result = login_vas()
    print(f"login_vas() result with date input not filled: {result!r}")  # Expect None

if __name__ == '__main__':
    test_date_input_not_filled()
