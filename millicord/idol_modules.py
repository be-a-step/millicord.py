import yaml
from typing import Tuple, Union, Optional, List
from .modules.utils.module_base import IdolModuleBase, IdolModuleType
from pathlib import Path
from .modules.utils.idol_exceptions import IdolModuleError
from .modules.utils.idol_base import IdolBase
from .modules.utils.setting import IdolConfig, IdolScript
from . import modules
from .modules.utils.functions import get_module_identifier


class IdolModules(object):
    def __init__(self):
        self.modules: List[IdolModuleType] = [IdolBase]
        self.module_identifiers = [get_module_identifier(IdolBase)]

    @classmethod
    def load_from_yaml(cls, path: Union[Path, str]):
        idol_modules = cls()
        with Path(path).open() as f:
            module_dict = yaml.load(f)
            for module_name in module_dict.get('internal', []):
                if module_name == 'IdolBase':
                    continue
                module = getattr(modules, module_name, None)
                if module is None:
                    raise ValueError('No module named {} exists'.format(module_name))
                idol_modules.add(module)
            # todo: implement external modules loading
            # for module_name in modules.get('external', {}).keys():
            #     module = getattr(modules, module_name, None)
            #     if module is None:
            #         raise ValueError('No module named {} exists'.format(module_name))
            #     idol_modules.add(module)
            return idol_modules

    def write_to_yaml(self, path: Union[Path, str], default_flow_style=False, overwrite=False):
        path = Path(path)
        if (not overwrite) and path.exists():
            raise FileExistsError(path)
        with path.open('w') as f:
            # todo: implement external
            f.write(yaml.dump({'internal': self.module_identifiers}, default_flow_style=default_flow_style))

    def generate_default_config(self) -> IdolConfig:
        conf = IdolConfig()
        for module in self.modules:
            if len(module.DEFAULT_CONFIG):
                conf[get_module_identifier(module)] = module.DEFAULT_CONFIG
        return conf

    def generate_default_script(self) -> IdolScript:
        script = IdolScript()
        for module in self.modules:
            if len(module.DEFAULT_SCRIPT):
                script[get_module_identifier(module)] = module.DEFAULT_SCRIPT
        return script

    def find(self, key_identifier, return_idx=False) -> \
            Union[Tuple[Optional[int], Optional[IdolModuleType]], IdolModuleType, None]:
        for i, module_identifier in enumerate(self.module_identifiers):
            if key_identifier == module_identifier:
                return (i, self.modules[i]) if return_idx else self.modules[i]
        return (None, None) if return_idx else None

    def add(self, new_module: IdolModuleType):
        if not issubclass(new_module, IdolModuleBase):
            raise ValueError('Invalid Object {}.'.format(repr(new_module)))
        if new_module in self:
            return
        print('add module:', new_module.__name__)
        self.modules.append(new_module)
        self.module_identifiers.append(get_module_identifier(new_module))
        for req in new_module.MODULE_REQUIREMENTS:
            self.add(req)

    def to_tuple(self) -> Tuple:
        return tuple(self.modules)

    def __contains__(self, item):
        if issubclass(item, IdolModuleBase):
            return get_module_identifier(item) in self.module_identifiers
        elif isinstance(item, str):
            return item in self.module_identifiers
        return False
