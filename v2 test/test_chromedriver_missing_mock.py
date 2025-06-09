from unittest.mock import patch
from selenium.common.exceptions import WebDriverException
from main import login_and_test_v2

@patch('main.webdriver.Chrome')
def test_chromedriver_missing(mock_chrome):
    # Simulate ChromeDriver missing
    mock_chrome.side_effect = WebDriverException("ChromeDriver executable needs to be in PATH.")
    result = login_and_test_v2()
    print(f"login_and_test_v2() result with missing ChromeDriver: {result!r}")  # Expect None

if __name__ == '__main__':
    test_chromedriver_missing()
