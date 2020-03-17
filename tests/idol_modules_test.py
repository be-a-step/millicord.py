import unittest
from millicord.idol_modules import IdolModules
from millicord.utils.module_base import IdolModuleBase, IdolModuleType
from millicord.utils.idol_base import IdolBase, IdolBaseType
from pathlib import Path
from typing import Union
import os
import shutil


class SampleModule1(IdolModuleBase):
    MODULE_REQUIREMENTS = []
    DEFAULT_CONFIG = {
        'module1_conf_key': 'module1_conf_value'
    }


class SampleModule2(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        SampleModule1
    }
    DEFAULT_SCRIPT = {
        'module2_script_key': 'module2_script_value'
    }


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


class SampleModule4(IdolModuleBase):
    pass


DEFAULT_CONFIG = {
    'SampleModule1':
        {'module1_conf_key': 'module1_conf_value'},
    'SampleModule3':
        {'module3_conf_key': 'module3_conf_value'}
}

DEFAULT_SCRIPT = {
    'SampleModule2':
        {'module2_script_key': 'module2_script_value'},
    'SampleModule3':
        {'module3_script_key': 'module3_script_value'}
}

MODULES_YAML = '\
internal:\n\
- IdolBase\n\
- SampleModule1\n\
- SampleModule2\n\
- SampleModule3\n\
'


class TestIdolModulesCoreMethods(unittest.TestCase):
    """
    Note ---- TestIdolModulesではTestIdolModules.setUp()に
    IdolModules.__init__()
    とIdolModules.add()
    を必要とするので、これらのメソッドのみこちらでテストする。
    """

    def assertHavingModule(self,
                           idol_modules: IdolModules,
                           *modules: Union[IdolModuleType,
                                           IdolBaseType]):
        self.assertEqual(idol_modules.modules, list(modules))
        self.assertEqual(
            idol_modules.module_identifiers, [
                m.__name__ for m in modules])

    def test_init(self):
        self.assertHavingModule(IdolModules(), IdolBase)

    def test_add(self):
        idol_modules = IdolModules()
        idol_modules.add(SampleModule1)
        self.assertHavingModule(idol_modules, IdolBase, SampleModule1)

        idol_modules = IdolModules()
        idol_modules.add(SampleModule2)
        self.assertHavingModule(
            idol_modules,
            IdolBase,
            SampleModule1,
            SampleModule2
        )

        idol_modules = IdolModules()
        idol_modules.add(SampleModule3)
        self.assertHavingModule(
            idol_modules,
            IdolBase,
            SampleModule1,
            SampleModule2,
            SampleModule3
        )

        idol_modules = IdolModules()
        idol_modules.add(SampleModule3)
        idol_modules.add(SampleModule1)
        idol_modules.add(SampleModule2)
        self.assertHavingModule(
            idol_modules,
            IdolBase,
            SampleModule1,
            SampleModule2,
            SampleModule3
        )

        idol_modules = IdolModules()
        self.assertRaises(ValueError, idol_modules.add, 'hoge')
        self.assertRaises(ValueError, idol_modules.add, 2)


class TestIdolModules(unittest.TestCase):
    def setUp(self):
        self.idol_modules = IdolModules()
        for module in [
            SampleModule3,
            SampleModule2,
            SampleModule1
        ]:
            self.idol_modules.add(module)
        self.write_dir: Path = Path(
            __file__).parent / 'tmp/test_idol_modules_file_io'
        os.makedirs(str(self.write_dir))

    def tearDown(self):
        shutil.rmtree(str(self.write_dir), ignore_errors=True)

    def test_to_tuple(self):
        self.assertEqual(
            self.idol_modules.to_tuple(),
            (IdolBase,
             SampleModule1,
             SampleModule2,
             SampleModule3)
        )

    def test_contains(self):
        self.assertTrue(SampleModule1 in self.idol_modules)
        self.assertTrue(SampleModule2 in self.idol_modules)
        self.assertTrue(SampleModule3 in self.idol_modules)
        self.assertFalse(SampleModule4 in self.idol_modules)
        self.assertTrue('SampleModule1' in self.idol_modules)
        self.assertTrue('SampleModule2' in self.idol_modules)
        self.assertTrue('SampleModule3' in self.idol_modules)
        self.assertFalse('SampleModule4' in self.idol_modules)

    def test_generate_default_config(self):
        default_config = self.idol_modules.generate_default_config()
        self.assertEqual(default_config, DEFAULT_CONFIG)

    def test_generate_default_script(self):
        default_script = self.idol_modules.generate_default_script()
        self.assertEqual(default_script, DEFAULT_SCRIPT)

    def test_write_to_yaml(self):
        yaml_file_path = self.write_dir / 'modules.yaml'
        self.idol_modules.write_to_yaml(yaml_file_path)
        with yaml_file_path.open() as f:
            self.assertEqual(f.read(), MODULES_YAML)

    # def test_load_from_yaml(self):
    #     # todo: 外部モジュール取り込みを実装して、このテストを実行可能とする
    #     yaml_file_path = self.write_dir / 'modules.yaml'
    #     with yaml_file_path.open('w') as f:
    #         f.write(MODULES_YAML)
    #     self.assertEqual(
    #         self.idol_modules.modules,
    #         IdolModules.load_from_yaml(yaml_file_path).modules
    #     )


if __name__ == '__main__':
    unittest.main()
