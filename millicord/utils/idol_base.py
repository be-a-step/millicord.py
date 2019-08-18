from typing import Type, Union
from pathlib import Path
from .idol_exceptions import IdolSettingError
from discord import Client
from .setting import IdolScriptType, IdolScriptItemType, IdolConfigType, IdolConfigItemType
from .module_base import IdolModuleType, IdolModuleBase


class IdolBase(Client, IdolModuleBase):
    def __init__(
            self,
            config: IdolConfigType,
            script: IdolScriptType,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.script = script

    def find_config(self, module: IdolModuleType,
                    path: Union[Path, str]) -> IdolConfigItemType:
        module_identifier = module.get_identifier()
        item = self.config.find_by_path(Path(module_identifier, path))
        if item is None:
            raise IdolSettingError(
                'config {} is required but not written in the yaml file.'.format(path))
        return item

    def find_script(
            self,
            module: IdolModuleType,
            path: Path) -> IdolScriptItemType:
        module_identifier = module.get_identifier()
        item = self.script.find_by_path(Path(module_identifier, path))
        if item is None:
            raise IdolSettingError(
                'script {} is required but not written in the yaml file.'.format(path))
        return item


IdolBaseType = Type[IdolBase]
