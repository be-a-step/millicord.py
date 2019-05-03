from typing import Union, Optional
from pathlib import Path
import types
from .idol_modules import IdolModules
from .modules.utils.setting import IdolConfig, IdolScript
from .modules.utils.idol_exceptions import IdolConfigError, IdolScriptError, IdolModuleError
from .modules.utils.module_base import IdolModuleType


class IdolBuilder(object):
    def __init__(self, token: Optional[str] = None, name: Optional[str] = None):
        self.path = None
        self.name = name
        self.token = token
        self.modules = IdolModules()
        self.script = IdolScript()
        self.config = IdolConfig()

    @classmethod
    def load_from_folder(cls, path: Union[Path, str], name: str = None):
        builder = cls()
        if not path.is_dir():
            raise ValueError('You must pass a path of an existing directory.')
        builder.name = name or path.stem
        builder.token = (path / '.token').open().read().strip()
        builder.load_modules_from_yaml(path)
        builder.load_config_from_yaml(path)
        builder.load_script_from_yaml(path)

    def load_modules_from_yaml(self, path: Union[Path, str]):
        self.modules = IdolModules.load_from_yaml(path)

    def load_script_from_yaml(self, path: Union[Path, str]):
        self.script = IdolScript.load_from_yaml(path)

    def load_config_from_yaml(self, path: Union[Path, str]):
        self.config = IdolConfig.load_from_yaml(path)

    def build_check(self):
        for module in self.modules.modules:
            if sum(rm not in self.modules for rm in module.MODULE_REQUIREMENTS) > 0:
                raise IdolModuleError()
            if sum(self.script.get(dsk, None) is None for dsk in module.DEFAULT_SCRIPT.keys()) > 0:
                raise IdolScriptError()
            if sum(self.config.get(dck, None) is None for dck in module.DEFAULT_CONFIG.keys()) > 0:
                raise IdolConfigError()
        return True

    def build(self):
        self.build_check()
        idol_cls = types.new_class(self.name, self.modules.to_tuple())
        return idol_cls(self.config, self.script)

    def add_module(self, module: IdolModuleType):
        self.modules.add(module)
