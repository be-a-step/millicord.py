import unittest
from millicord.utils.module_base import IdolModuleBase
from pathlib import Path
import shutil
from tests import utils


class SampleModule1(IdolModuleBase):
    async def on_ready(self):
        await self.logout()


class TestGenerateIdolFolder(utils.AsyncTestMixin, unittest.TestCase):
    def setUp(self):
        super()
        self.idol_path = Path(__file__).parent / 'idols/idol_test_idol'
        token_path = Path(__file__).parent / 'idols/idol_test_token/.token'
        with token_path.open() as f:
            self.token = f.read().strip()

    # def test_generate_idol_folder(self):
    #     # todo: load from external
    #     generate_idol_folder(
    #         self.idol_path,
    #         self.token,
    #         [SampleModule1],
    #         False
    #     )
    #     IdolBuilder.load_from_folder(
    #         self.idol_path).build_and_run(
    #         self.get_event_loop())
    #
    #     self.assertRaises(
    #         FileExistsError,
    #         generate_idol_folder,
    #         self.idol_path,
    #         self.token,
    #         [SampleModule1],
    #         False
    #     )
    #
    #     self.assertRaises(
    #         ValueError,
    #         generate_idol_folder,
    #         self.idol_path,
    #         self.token,
    #         [1],
    #         True
    #     )
    #     self.assertTrue(self.idol_path.exists())

    def tearDown(self):
        shutil.rmtree(self.idol_path)
