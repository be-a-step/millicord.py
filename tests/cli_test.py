import unittest
from click.testing import CliRunner
from millicord.cli import launch_idol_from_file, generate_template


def test_launch_idol_from_file():
    runner = CliRunner()
    result = runner.invoke(hello, ['Peter'])
    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'
