import unittest
from millicord.idol_modules import IdolModules
from millicord.modules.utils.module_base import IdolModuleBase, IdolModuleType
from millicord.modules.utils.idol_base import IdolBase, IdolBaseType
from millicord.idol_builder import IdolBuilder
from pathlib import Path
from typing import Union
import yaml
import os
import shutil
from millicord.idol import generate_idol_folder
from . import utils


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
