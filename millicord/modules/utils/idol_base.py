from typing import Type, Union
from pathlib import Path
from .idol_exceptions import IdolSettingError
from discord import Client
from .setting import IdolScriptType, IdolScriptItemType, IdolConfigType, IdolConfigItemType


class IdolBase(Client):
    # constants for compatibility (DO NOT ADD ANYTHING!!)
    MODULE_REQUIREMENTS = []
    DEFAULT_CONFIG = {}
    DEFAULT_SCRIPT = {}

    def __init__(self, config: IdolConfigType, script: IdolScriptType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idol_state = None
        self.config = config
        self.script = script

    def find_config(self, path: Union[Path, str]) -> IdolConfigItemType:
        item = self.config.find_by_path(Path(path))
        if item is None:
            raise IdolSettingError('config {} is required but not written in the yaml file.'.format(path))
        return item

    def find_script(self, path: Path) -> IdolScriptItemType:
        item = self.script.find_by_path(Path(path))
        if item is None:
            raise IdolSettingError('script {} is required but not written in the yaml file.'.format(path))
        return item

IdolBaseType = Type[IdolBase]
