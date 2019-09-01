from typing import Type, Union, Any
from pathlib import Path
from .idol_exceptions import IdolSettingError
from discord import Client
from millicord.utils.setting import IdolScript, IdolConfig
from .module_base import IdolModuleType, IdolModuleBase


class IdolBase(Client, IdolModuleBase):
    """
    Idolオブジェクトの基底となるクラス。
    このクラスにIdolModuleクラスをMix-inする形でIdolインスタンスが生成される。
    そのため、IdolBuilderを使わずに直接インスタンス化されることはない。

    Attributes
    ----------
    config : IdolConfig
        Idolのモジュールのコンフィグ
    script : IdolScript
        Idolのモジュールのスクリプト
    """

    def __init__(
            self,
            config: IdolConfig,
            script: IdolScript,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.script = script

    def find_config(
            self,
            module: IdolModuleType,
            path: Union[Path, str]) -> Any:
        """
        あるIdolModuleに紐づいたconfigを探索

        Parameters
        ----------
        module : Type[IdolModuleBase]
            対象のモジュール
        path : Union[Path, str]
            module_identifier以下のパス

        Returns
        -------
        config : IdolConfigItemType
        """
        module_identifier = module.get_identifier()
        item = self.config.find_by_path(Path(module_identifier, path))
        if item is None:
            raise IdolSettingError(
                'config {} is required but not written in the yaml file.'.format(path))
        return item

    def find_script(self, module: IdolModuleType, path: Path) -> str:
        """
        あるIdolModuleに紐づいたscriptを探索

        Parameters
        ----------
        module : IdolModuleBase
            対象のモジュール
        path : Union[Path, str]
            module_identifier以下のパス

        Returns
        -------
        config : IdolConfigItemType
        """
        module_identifier = module.get_identifier()
        item = self.script.find_by_path(Path(module_identifier, path))
        if item is None:
            raise IdolSettingError(
                'script {} is required but not written in the yaml file.'.format(path))
        return item


IdolBaseType = Type[IdolBase]
