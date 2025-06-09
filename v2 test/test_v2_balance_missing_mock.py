from unittest.mock import patch, MagicMock
from selenium.common.exceptions import NoSuchElementException
from main import login_and_test_v2

# Patch the webdriver to mock find_element to raise NoSuchElementException for the balance element
@patch('main.webdriver.Chrome')
def test_missing_balance_element(mock_chrome):
    # Mock driver instance
    mock_driver = MagicMock()
    # Normal behavior for login fields
    def find_element_side_effect(by, value):
        # Raise for the balance element only
        if by == 'xpath' and 'Balance:' in value:
            raise NoSuchElementException('No such element: balance')
        return MagicMock()
    mock_driver.find_element.side_effect = find_element_side_effect
    mock_chrome.return_value = mock_driver

    result = login_and_test_v2()
    print(f"login_and_test_v2() result when balance element missing: {result!r}")  # Expect None

if __name__ == '__main__':
    test_missing_balance_element()
