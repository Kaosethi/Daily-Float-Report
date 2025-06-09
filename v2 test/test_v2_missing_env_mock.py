import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch
from main import login_and_test_v2

@patch('main.os.getenv')
def test_missing_env(mock_getenv):
    # Simulate missing V2_USERNAME and V2_PASSWORD
    def getenv_side_effect(key, default=None):
        if key in ("V2_USERNAME", "V2_PASSWORD"):
            return None
        return default
    mock_getenv.side_effect = getenv_side_effect
    result = login_and_test_v2()
    print(f"login_and_test_v2() result with missing env variables: {result!r}")  # Expect None

if __name__ == '__main__':
    test_missing_env()
