import unittest
from millicord.idol_modules import IdolModules
from millicord.utils.module_base import IdolModuleBase
from millicord.utils.idol_base import IdolBase
from millicord.utils.idol_exceptions import IdolScriptError, IdolConfigError, IdolBaseError
from millicord.idol_builder import IdolBuilder
from millicord.utils.setting import IdolConfig, IdolScript
from pathlib import Path
import copy
from tests import utils


class SampleModule1(IdolModuleBase):
    MODULE_REQUIREMENTS = []
    DEFAULT_CONFIG = {
        'module1_conf_key': 'module1_conf_value'
    }

    async def on_ready(self):
        self.cor_str = ''
        self.func_str = ''
        self.cor_ret_str = await super(SampleModule1, self).on_ready_sub('')
        self.func_ret_str = super(SampleModule1, self).test_func_sub('')
        await self.logout()

    async def on_error(self, event_method, *args, **kwargs):
        raise Exception('raised in {}'.format(repr(event_method)))


class SampleModule2(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        SampleModule1
    }
    DEFAULT_SCRIPT = {
        'module2_script_key': 'module2_script_value'
    }

    async def on_ready_sub(self, s: str):
        self.cor_str += 'hoge'
        sc = self.chain_super_coroutine('on_ready_sub', SampleModule2)
        s += "ho"
        return await sc(s) or s

    def test_func_sub(self, s: str):
        self.func_str += 'foo'
        sf = self.chain_super_function('test_func_sub', SampleModule2)
        s += "fo"
        return sf(s) or s


class SampleModule3(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        SampleModule2,
        SampleModule1
    }
    DEFAULT_CONFIG = {
        'module3_conf_key': 'module3_conf_value'
    }
    DEFAULT_SCRIPT = {
        'module3_script_key': 'module3_script_value'
    }

    async def on_ready_sub(self, s: str):
        self.cor_str += 'fuga'
        sc = self.chain_super_coroutine('on_ready_sub', SampleModule3)
        s += "ge"
        return await sc(s) or s

    def test_func_sub(self, s: str):
        self.func_str += 'bar'
        sf = self.chain_super_function('test_func_sub', SampleModule3)
        s += 'o'
        return sf(s) or s


EXPECTED_MODULES = [
    IdolBase, SampleModule1, SampleModule2, SampleModule3
]

EXPECTED_CONFIG = {
    'SampleModule1':
        {'module1_conf_key': 'module1_conf_value'},
    'SampleModule3':
        {'module3_conf_key': 'module3_conf_value'}
}

EXPECTED_SCRIPT = {
    'SampleModule2':
        {'module2_script_key': 'module2_script_value'},
    'SampleModule3':
        {'module3_script_key': 'module3_script_value'}
}


class IdolBuilderTest(utils.AsyncTestMixin, unittest.TestCase):
    def setUp(self):
        self.idol_path = Path(__file__).parent / \
            'idols/idol_builder_test_idol/'
        super().setUp()

    def test_add_module(self):
        builder = IdolBuilder()
        builder.add_module(SampleModule1)
        self.assertEqual(builder.modules.modules, [IdolBase, SampleModule1])

    def test_build_check(self):
        modules = IdolModules()
        modules.add(SampleModule3)
        script = modules.generate_default_script()
        config = modules.generate_default_config()

        IdolBuilder(modules=modules, script=script, config=config)

        builder = IdolBuilder(
            modules=modules,
            script=script,
            config=IdolConfig()
        )
        self.assertRaises(
            IdolConfigError,
            builder.build_check
        )

        builder = IdolBuilder(
            modules=modules,
            script=IdolScript(),
            config=config
        )
        self.assertRaises(
            IdolScriptError,
            builder.build_check
        )

        builder = IdolBuilder(
            modules=modules,
            script=IdolScript(),
            config=IdolConfig()
        )
        self.assertRaises(
            (IdolScriptError, IdolConfigError),
            builder.build_check)

        modules_without_base = copy.deepcopy(modules)
        modules_without_base.modules = modules_without_base.modules[1:]
        builder = IdolBuilder(
            modules=modules_without_base,
            script=script,
            config=config
        )
        self.assertRaises(
            IdolBaseError,
            builder.build_check
        )

    # def test_load_modules_from_yaml(self):
    #     # todo: load from external
    #     builder = IdolBuilder()
    #     builder.load_modules_from_yaml(self.idol_path / 'modules.yaml')
    #     self.assertEqual(builder.modules, EXPECTED_MODULES)

    def test_load_script_from_yaml(self):
        builder = IdolBuilder()
        builder.load_script_from_yaml(self.idol_path / 'script.yaml')
        self.assertEqual(builder.script.data, EXPECTED_SCRIPT)

    def test_load_config_from_yaml(self):
        builder = IdolBuilder()
        builder.load_config_from_yaml(self.idol_path / 'config.yaml')
        self.assertEqual(builder.config.data, EXPECTED_CONFIG)

    def test_load_from_folder(self):
        # todo: load from external
        self.assertRaises(
            ValueError,
            IdolBuilder.load_from_folder,
            self.idol_path / 'modules.yaml'
        )
        self.assertRaises(
            ValueError,
            IdolBuilder.load_from_folder,
            self.idol_path / 'not_existing_folder'
        )
        # builder = IdolBuilder.load_from_folder(self.idol_path)
        # self.assertEqual(builder.name, 'idol_builder_test_idol')
        # self.assertIsInstance(builder.token, str)
        # self.assertEqual(builder.config.data, EXPECTED_CONFIG)
        # self.assertEqual(builder.script.data, EXPECTED_SCRIPT)
        # self.assertEqual(builder.modules, EXPECTED_MODULES)

    def test_build(self):
        modules = IdolModules()
        modules.add(SampleModule3)
        script = modules.generate_default_script()
        config = modules.generate_default_config()
        with (self.idol_path / '.token').open() as f:
            token = f.read().strip()

        builder = IdolBuilder(
            modules=modules,
            script=script,
            config=config,
            name='idol_builder_test_idol',
            token=token
        )
        idol = builder.build(loop=self.get_event_loop())
        idol.run(builder.token)
        self.assertEqual(idol.cor_str, 'hogefuga')
        self.assertEqual(idol.cor_ret_str, 'hoge')
        self.assertEqual(idol.func_str, 'foobar')
        self.assertEqual(idol.func_ret_str, 'foo')

    def test_build_and_run(self):
        modules = IdolModules()
        modules.add(SampleModule3)
        script = modules.generate_default_script()
        config = modules.generate_default_config()
        with (self.idol_path / '.token').open() as f:
            token = f.read().strip()

        builder = IdolBuilder(
            modules=modules,
            script=script,
            config=config,
            name='idol_builder_test_idol',
            token=token
        )
        builder.build_and_run(loop=self.get_event_loop())
