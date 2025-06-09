import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from main2 import setup_driver

def test_setup_driver_download_dir():
    with patch('main2.Options') as MockOptions, patch('main2.webdriver.Chrome') as MockChrome:
        mock_options = MagicMock()
        MockOptions.return_value = mock_options
        MockChrome.return_value = MagicMock()  # Prevent real Chrome launch
        custom_dir = 'custom_downloads'
        setup_driver(download_dir=custom_dir)
        # Check that download.default_directory is set correctly
        prefs = None
        for call in mock_options.add_experimental_option.call_args_list:
            if call[0][0] == 'prefs':
                prefs = call[0][1]
        print(f"Chrome prefs: {prefs}")
        assert prefs is not None and prefs.get('download.default_directory', None) == os.path.abspath(custom_dir), "Download directory not set correctly!"
        print("Test passed: Download directory is set correctly.")

if __name__ == '__main__':
    test_setup_driver_download_dir()
