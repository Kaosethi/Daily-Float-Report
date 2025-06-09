import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import setup_driver

def test_setup_driver_headless():
    with patch('main2.Options') as MockOptions, patch('main2.webdriver.Chrome') as MockChrome:
        mock_options = MagicMock()
        MockOptions.return_value = mock_options
        MockChrome.return_value = MagicMock()  # Prevent real Chrome launch
        setup_driver(download_dir='downloads')
        # Collect all arguments passed to add_argument
        args = [call[0][0] for call in mock_options.add_argument.call_args_list]
        print(f"Chrome arguments: {args}")
        assert '--headless' in args, "Headless mode not enabled!"
        print("Test passed: Headless mode is enabled.")

if __name__ == '__main__':
    test_setup_driver_headless()
