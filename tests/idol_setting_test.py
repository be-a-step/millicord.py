import unittest
import os

from millicord.idol import IdolSetting, IdolScheduler, IdolProcess
import datetime




TEST_YML = os.path.join(os.path.dirname(__file__), 'idols', 'testbot.yml')
class TestIdolSetting(unittest.TestCase):
    def setUp(self):
        self.setting = IdolSetting(TEST_YML)

    def assertEqualDict(self, query, target=None):
        target = self.setting._setting_dict if target is None else target
        for k, v in query.items():
            if isinstance(v, dict):
                self.assertEqualDict(v, target[k])
            else:
                self.assertEqual(v, target[k])

    def test_load(self):
        self.assertEqualDict(
                {
                    'name': 'テストボット',
                    'tokenfile': 'envs/testbot.env',
                    'P-call': 'P',
                    'attending_time': '08:00:00',
                    'leaving_time': '19:00:00',
                    'actions': {
                        'greeting':{
                            'rooms': ['控え室'],
                            'lines': {
                                    'attending': 'おはようございます',
                                    'leaving': 'お疲れ様でした'
                                }

                                }
                            }
                        }
        )


class TestIdolManager(unittest.TestCase):
    def setUp(self):
        self.manager = IdolScheduler()

    def test_load(self):
        self.manager.load_idol(TEST_YML)

    def test_load_dir(self):
        self.manager.load_from_directory(os.path.dirname(TEST_YML))
        self.assertEqual(list(self.manager.idols.keys()), ['testbot'])

if __name__ == '__main__':
    unittest.main()
