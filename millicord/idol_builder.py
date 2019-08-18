from typing import Union, Optional
from pathlib import Path
import types
from .idol_modules import IdolModules
from millicord.utils.setting import IdolConfig, IdolScript
from millicord.utils.idol_exceptions import IdolConfigError, IdolScriptError, IdolModuleError, IdolBaseError
from millicord.utils.module_base import IdolModuleType
from millicord.utils.idol_base import IdolBase
from millicord.utils.functions import get_module_identifier
import inspect


class IdolBuilder(object):
    def __init__(self, token: Optional[str] = None, name: Optional[str] = None,
                 modules: Optional[IdolModules] = None,
                 script: Optional[IdolScript] = None,
                 config: Optional[IdolConfig] = None):
        self.name = name
        self.token = token
        self.modules = modules or IdolModules()
        self.script = script or IdolScript()
        self.config = config or IdolConfig()

    @classmethod
    def load_from_folder(cls, path: Union[Path, str], name: str = None):
        path = Path(path)
        builder = cls()
        if not path.is_dir():
            raise ValueError('You must pass a path of an existing directory.')
        builder.name = name or path.stem
        with (path / '.token').open() as f:
            builder.token = f.read().strip()
        builder.load_modules_from_yaml(path / 'modules.yaml')
        builder.load_config_from_yaml(path / 'config.yaml')
        builder.load_script_from_yaml(path / 'script.yaml')
        return builder

    def load_modules_from_yaml(self, path: Union[Path, str]):
        self.modules = IdolModules.load_from_yaml(path)

    def load_script_from_yaml(self, path: Union[Path, str]):
        self.script = IdolScript.load_from_yaml(path)

    def load_config_from_yaml(self, path: Union[Path, str]):
        self.config = IdolConfig.load_from_yaml(path)

    def build_check(self):
        if not (inspect.isclass(self.modules.modules[0])
                and issubclass(self.modules.modules[0], IdolBase)):
            raise IdolBaseError()
        for module in self.modules.modules:
            if sum(rm not in self.modules for rm in module.MODULE_REQUIREMENTS) > 0:
                raise IdolModuleError()
            if sum(
                self.script.get(
                    get_module_identifier(module),
                    {}
                ).get(dsk, None) is None
                    for dsk in module.DEFAULT_SCRIPT.keys()) > 0:
                raise IdolScriptError()
            if sum(
                self.config.get(
                    get_module_identifier(module),
                    {}
                ).get(dck, None) is None
                    for dck in module.DEFAULT_CONFIG.keys()) > 0:
                raise IdolConfigError()
        return True

    def build(self, loop=None):
        self.build_check()
        idol_cls = types.new_class(self.name, self.modules.to_tuple())
        return idol_cls(self.config, self.script, loop=loop)

    def build_and_run(self, loop=None):
        self.build(loop=loop).run(self.token)

    def add_module(self, module: IdolModuleType):
        self.modules.add(module)
