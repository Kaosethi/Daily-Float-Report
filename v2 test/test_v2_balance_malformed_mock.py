from unittest.mock import patch, MagicMock
from main import login_and_test_v2

@patch('main.webdriver.Chrome')
def test_malformed_balance_text(mock_chrome):
    mock_driver = MagicMock()
    # Mock normal login fields
    def find_element_side_effect(by, value):
        # Mock the balance element
        if by == 'xpath' and 'Balance:' in value:
            balance_elem = MagicMock()
            balance_elem.text = "Balance: XX.XX USD"  # Malformed text
            return balance_elem
        return MagicMock()
    mock_driver.find_element.side_effect = find_element_side_effect
    mock_chrome.return_value = mock_driver

    result = login_and_test_v2()
    print(f"login_and_test_v2() result with malformed balance text: {result!r}")  # Expect None

if __name__ == '__main__':
    test_malformed_balance_text()
