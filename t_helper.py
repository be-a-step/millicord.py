import argparse
import unittest
from pathlib import Path
import os

parser = argparse.ArgumentParser(description='テスト実行用スクリプト')

parser.add_argument('-r', '--run', action='store_true', help='テスト実行')
parser.add_argument('-t', '--deploy-token', help='テストで使用するidolのトークンをdeploy')
args = parser.parse_args()

TEST_DIR = Path(__file__).parent / "tests"
TEST_IDOLS_DIR = TEST_DIR / 'idols'
TOKEN_REQUIRED_IDOLS = [
    'idol_base_test_idol',
    'module_base_test_idol',
    'idol_test_token'
]


if __name__ == '__main__':
    if args.deploy_token is not None:
        for idol in TOKEN_REQUIRED_IDOLS:
            if not (TEST_IDOLS_DIR / idol).exists():
                os.makedirs(str(TEST_IDOLS_DIR / idol))
            with (TEST_IDOLS_DIR / idol / '.token').open('w') as f:
                f.write(args.deploy_token)
                print('export token to:')
                print(TEST_IDOLS_DIR / idol / '.token')

    if args.run:
        loader = unittest.TestLoader()
        test = loader.discover(TEST_DIR, pattern='*_test.py')
        runner = unittest.TextTestRunner()
        runner.run(test)
