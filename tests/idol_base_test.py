import unittest
from millicord.utils.idol_base import IdolBase
from millicord.utils.setting import IdolConfig, IdolScript
from pathlib import Path
import asyncio
from . import utils


class SampleModule1(object):
    pass


class SampleModule2(object):
    pass


class IdolBaseForTest(IdolBase, SampleModule1, SampleModule2):
    async def on_ready(self):
        await asyncio.sleep(3)
        await self.logout()

    async def on_error(self, event_method, *args, **kwargs):
        raise Exception('raised in {}'.format(repr(event_method)))


class TestIdolBase(utils.AsyncTestMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.idol_path = Path(__file__).parent / 'idols/idol_base_test_idol/'
        self.idol = IdolBaseForTest(
            script=IdolScript.load_from_yaml(self.idol_path / 'script.yaml'),
            config=IdolConfig.load_from_yaml(self.idol_path / 'config.yaml'),
            loop=self.get_event_loop())

    def test_launch(self):
        with (self.idol_path / '.token').open() as f:
            token = f.read().strip()
        self.idol.run(token)

    def test_find_config(self):
        self.assertEqual(
            self.idol.find_config(
                SampleModule1, ''), {
                'key': 'config1'})
        self.assertEqual(
            self.idol.find_config(
                SampleModule1, 'key'), 'config1')
        self.assertEqual(
            self.idol.find_config(
                SampleModule2, ''), {
                'key': 'config2'})

    def test_find_script(self):
        self.assertEqual(
            self.idol.find_script(
                SampleModule1, ''), {
                'key': 'script1'})
        self.assertEqual(
            self.idol.find_script(
                SampleModule1, 'key'), 'script1')
        self.assertEqual(
            self.idol.find_script(
                SampleModule2, ''), {
                'key': 'script2'})
