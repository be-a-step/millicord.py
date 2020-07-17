import unittest
from millicord.utils.idol_base import IdolBase
from millicord.utils.module_base import IdolModuleBase
from pathlib import Path
import asyncio

from . import utils


class SampleModule1(IdolModuleBase):
    async def on_ready_sub(self, s: str):
        self.cor_str += 'hoge'
        sc = self.chain_super_coroutine('on_ready_sub', SampleModule1)
        s += "ho"
        return await sc(s) or s

    def test_func_sub(self, s: str):
        self.func_str += 'foo'
        sf = self.chain_super_function('test_func_sub', SampleModule1)
        s += "fo"
        return sf(s) or s


class SampleModule2(IdolModuleBase):
    async def on_ready_sub(self, s: str):
        self.cor_str += 'fuga'
        sc = self.chain_super_coroutine('on_ready_sub', SampleModule2)
        s += "ge"
        return await sc(s) or s

    def test_func_sub(self, s: str):
        self.func_str += 'bar'
        sf = self.chain_super_function('test_func_sub', SampleModule2)
        s += 'o'
        return sf(s) or s


class TestIdol(IdolBase, SampleModule1, SampleModule2):
    async def on_ready(self):
        self.cor_str = ''
        self.func_str = ''
        self.cor_ret_str = await super(TestIdol, self).on_ready_sub('')
        self.func_ret_str = super(TestIdol, self).test_func_sub('')
        await self.logout()

    async def on_error(self, event_method, *args, **kwargs):
        raise Exception('raised in {}'.format(repr(event_method)))


class TestModuleBase(utils.AsyncTestMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.idol_path = Path(__file__).parent / 'idols/module_base_test_idol/'
        self.idol = TestIdol(
            script=None,
            config=None,
            loop=self.get_event_loop())

    def test_chain(self):
        with (self.idol_path / '.token').open() as f:
            token = f.read().strip()
        self.idol.run(token)
        self.assertEqual(self.idol.cor_str, 'hogefuga')
        self.assertEqual(self.idol.cor_ret_str, 'hoge')
        self.assertEqual(self.idol.func_str, 'foobar')
        self.assertEqual(self.idol.func_ret_str, 'foo')


if __name__ == '__main__':
    unittest.main()
