import unittest
from millicord.utils.idol_base import IdolBase
from millicord.utils.module_base import IdolModuleBase
from pathlib import Path
import asyncio


class SampleModule1(IdolModuleBase):
    async def on_ready_sub(self, s: str):
        self.cor_test_str += 'hoge'
        return await self.chain_super_coroutine('on_ready_sub', SampleModule1)(s + 'ho')

    def test_func_sub(self, s: str):
        self.func_test_str += 'foo'
        return self.chain_super_function(
            'test_func_sub',
            SampleModule1)(
            s + 'fo')


class SampleModule2(IdolModuleBase):
    async def on_ready_sub(self, s: str):
        self.cor_test_str += 'fuga'
        return await self.chain_super_coroutine('on_ready_sub', SampleModule2)(s + 'ge')

    def test_func_sub(self, s: str):
        self.func_test_str += 'bar'
        return self.chain_super_function(
            'test_func_sub',
            SampleModule2)(
            s + 'o')


class TestIdol(IdolBase, SampleModule1, SampleModule2):
    async def on_ready(self):
        args, kwargs = await super(TestIdol, self).on_ready_sub(self.cor_test_ret_str)
        self.cor_test_ret_str = args[0]
        args, kwargs = super(
            TestIdol, self).test_func_sub(
            self.func_test_ret_str)
        self.func_test_ret_str = args[0]
        await self.logout()

    async def on_error(self, event_method, *args, **kwargs):
        raise Exception('raised in {}'.format(repr(event_method)))


class TestModuleBase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.idol_path = Path(__file__).parent / 'idols/module_base_test_idol/'
        asyncio.set_event_loop(None)
        self.idol = TestIdol(
            script=None,
            config=None,
            loop=self.loop)

    def test_chain(self):
        with (self.idol_path / '.token').open() as f:
            token = f.read().strip()
        self.idol.cor_test_str = ''
        self.idol.cor_test_ret_str = ''
        self.idol.func_test_str = ''
        self.idol.func_test_ret_str = ''
        self.idol.run(token)
        self.assertEqual(self.idol.cor_test_str, 'hogefuga')
        self.assertEqual(self.idol.cor_test_ret_str, 'hoge')
        self.assertEqual(self.idol.func_test_str, 'foobar')
        self.assertEqual(self.idol.func_test_ret_str, 'foo')


if __name__ == '__main__':
    unittest.main()
