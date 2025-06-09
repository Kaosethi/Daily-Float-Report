from unittest.mock import patch, MagicMock
from selenium.common.exceptions import NoSuchElementException
from main import login_and_test_v2

# Patch the webdriver to mock find_element to raise NoSuchElementException for 'email'
@patch('main.webdriver.Chrome')
def test_missing_email_field(mock_chrome):
    # Mock driver instance
    mock_driver = MagicMock()
    # Make find_element raise NoSuchElementException when searching for 'email'
    def side_effect(by, value):
        if by == 'id' and value == 'email':
            raise NoSuchElementException('No such element: email')
        return MagicMock()
    mock_driver.find_element.side_effect = side_effect
    mock_chrome.return_value = mock_driver

    result = login_and_test_v2()
    print(f"login_and_test_v2() result when email field missing: {result!r}")  # Expect None

if __name__ == '__main__':
    test_missing_email_field()
