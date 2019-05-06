import unittest
from millicord.modules.utils import setting
from pathlib import Path
from datetime import date, datetime
import os


class TestYamlBase(unittest.TestCase):
    SAMPLE_YAML_DICT = {'SampleModule1': {
        'int_param': 123, 'str_param': 'val1', 'list_param': [
            'val2-2', 'val2-3'], 'keyvalue_param': {
            'key1': 'val1', 'key2': 'val2'}, 'date_param': date(
            year=2002, month=12, day=14), 'datetime_param': datetime(
            year=2002, month=12, day=14, hour=10, minute=00, second=00)},
        'SampleModule2': {'param': 'val'}
    }

    def setUp(self):
        self.idol_dir: Path = Path(__file__).parent / 'idols/setting_test_idol'
        self.sample_yaml = setting.YamlBase.load_from_yaml(
            self.idol_dir / 'config.yaml')

    def test_load_from_yaml(self):
        self.assertEqual(list(self.sample_yaml.keys()), [
                         'SampleModule1', 'SampleModule2'])
        mod1 = self.sample_yaml['SampleModule1']
        self.assertEqual(
            mod1, self.SAMPLE_YAML_DICT)
        mod2 = self.sample_yaml['SampleModule2']
        self.assertEqual(mod2, {'param': 'val'})

    def test_write_to_yaml(self):
        with self.assertRaises(FileExistsError):
            self.sample_yaml.write_to_yaml(
                self.idol_dir / 'config.yaml',
                default_flow_style=False,
                overwrite=False)
        try:
            self.sample_yaml.write_to_yaml(
                self.idol_dir / 'config_copy.yaml',
                default_flow_style=False,
                overwrite=False)
            copied_sample_yaml = setting.YamlBase.load_from_yaml(
                self.idol_dir / 'config_copy.yaml')
            self.assertEqual(copied_sample_yaml, self.sample_yaml)
        finally:
            os.remove(str(self.idol_dir / 'config_copy.yaml'))

    def test_find_by_path(self):
        self.assertEqual(
            self.sample_yaml.find_by_path(''),
            self.SAMPLE_YAML_DICT)
        self.assertEqual(
            self.sample_yaml.find_by_path('/'),
            self.SAMPLE_YAML_DICT)
        self.assertEqual(
            self.sample_yaml.find_by_path('SampleModule2'), {
                'param': 'val'})
        self.assertEqual(self.sample_yaml.find_by_path(
            '/SampleModule2'), {'param': 'val'})
        self.assertEqual(self.sample_yaml.find_by_path(
            'SampleModule2/param'), 'val')


if __name__ == "__main__":
    unittest.main()
