from typing import Union, Optional
from pathlib import Path
import types
from .idol_modules import IdolModules
from millicord.utils.setting import IdolConfig, IdolScript
from millicord.utils.idol_exceptions import (
    IdolConfigError,
    IdolScriptError,
    IdolModuleError,
    IdolBaseError)
from millicord.utils.module_base import IdolModuleType
from millicord.utils.idol_base import IdolBase
import inspect


class IdolBuilder(object):
    """
    IdolオブジェクトのBuilder

    Attributes
    ----------
    token: Optional[str]
        discord bot トークン
    name: Optional[str]
    modules: IdolModules
    script: IdolScript
    config: IdolConfig]
    """

    def __init__(
            self,
            token: Optional[str] = None,
            name: Optional[str] = None,
            modules: Optional[IdolModules] = None,
            script: Optional[IdolScript] = None,
            config: Optional[IdolConfig] = None):
        self.name = name
        self.token = token
        self.modules = modules or IdolModules()
        self.script = script or IdolScript()
        self.config = config or IdolConfig()

    @classmethod
    def load_from_folder(cls, path, name=None):
        """
        フォルダ読み込み

        Parameters
        ----------
        path : Union[Path, str]
        name : str

        Returns
        -------
        builder : IdolBuilder
        """
        path = Path(path)
        builder = cls()
        if not path.is_dir():
            raise ValueError(f'Folder {path} not found.')
        builder.name = name or path.stem
        builder.token = (path / '.token').read_text().strip()
        builder.load_modules_from_yaml(path / 'modules.yaml')
        builder.load_config_from_yaml(path / 'config.yaml')
        builder.load_script_from_yaml(path / 'script.yaml')
        return builder

    def load_modules_from_yaml(self, path: Union[Path, str]):
        """yamlからIdolModulesロード"""
        self.modules = IdolModules.load_from_yaml(path)

    def load_script_from_yaml(self, path: Union[Path, str]):
        """yamlからIdolScriptロード"""
        self.script = IdolScript.load_from_yaml(path)

    def load_config_from_yaml(self, path: Union[Path, str]):
        """yamlからIDolConfigロード"""
        self.config = IdolConfig.load_from_yaml(path)

    def build_check(self):
        """モジュール、コンフィグ、スクリプトが不正でないか確認"""
        # IdolBaseが正しく挿入されているか確認
        if not inspect.isclass(self.modules[0]) \
                or not issubclass(self.modules[0], IdolBase):
            raise IdolBaseError()
        for module in self.modules.modules:
            # 必要な前提モジュール/Script/Configが揃っているか確認
            if sum(rm not in self.modules for rm in
                   module.MODULE_REQUIREMENTS) > 0:
                raise IdolModuleError()
            if sum(
                    self.script.get(
                        module.get_identifier(),
                        {}
                    ).get(dsk, None) is None
                    for dsk in module.DEFAULT_SCRIPT.keys()) > 0:
                raise IdolScriptError()
            if sum(
                    self.config.get(
                        module.get_identifier(),
                        {}
                    ).get(dck, None) is None
                    for dck in module.DEFAULT_CONFIG.keys()) > 0:
                raise IdolConfigError()

    def build(self, loop=None):
        """
        buildメソッド。
        モジュールを使ってIdolクラスを生成し、インスタンス化して返す。

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop

        Returns
        -------
        idol : Any

        """
        self.build_check()
        idol_cls = types.new_class(self.name, self.modules.to_tuple())
        return idol_cls(self.config, self.script, loop=loop)

    def build_and_run(self, loop=None):
        """
        build+runへのエイリアス

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop

        """
        self.build(loop=loop).run(self.token)

    def add_module(self, module: IdolModuleType):
        """IdolModules.addへのエイリアス"""
        self.modules.add(module)
