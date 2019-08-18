import yaml
from typing import Tuple, Union, List
from millicord.utils.module_base import IdolModuleBase, IdolModuleType
from pathlib import Path
from millicord.utils.idol_base import IdolBase
from millicord.utils.setting import IdolConfig, IdolScript
from . import modules
import inspect


class IdolModules(object):
    def __init__(self):
        self.modules: List[IdolModuleType] = [IdolBase]
        self.module_identifiers = [IdolBase.get_identifier()]

    @classmethod
    def load_from_yaml(cls, path: Union[Path, str]):
        idol_modules = cls()
        with Path(path).open() as f:
            module_dict = yaml.load(f, Loader=yaml.FullLoader)
            for module_name in module_dict.get('internal', []):
                if module_name == 'IdolBase':
                    continue
                module = getattr(modules, module_name, None)
                if module is None:
                    raise ValueError(
                        'No module named {} exists'.format(module_name))
                idol_modules.add(module)
            # todo: implement external modules loading
            # for module_name in modules.get('external', {}).keys():
            #     module = getattr(modules, module_name, None)
            #     if module is None:
            #         raise ValueError('No module named {} exists'.format(module_name))
            #     idol_modules.add(module)
            return idol_modules

    def write_to_yaml(self,
                      path: Union[Path,
                                  str],
                      default_flow_style=False,
                      overwrite=False):
        path = Path(path)
        if (not overwrite) and path.exists():
            raise FileExistsError(path)
        with path.open('w') as f:
            # todo: implement external
            f.write(yaml.dump({'internal': self.module_identifiers},
                              default_flow_style=default_flow_style))

    def generate_default_config(self) -> IdolConfig:
        conf = IdolConfig()
        for module in self.modules:
            if len(module.DEFAULT_CONFIG):
                conf[module.get_identifier()] = module.DEFAULT_CONFIG
        return conf

    def generate_default_script(self) -> IdolScript:
        script = IdolScript()
        for module in self.modules:
            if len(module.DEFAULT_SCRIPT):
                script[module.get_identifier()] = module.DEFAULT_SCRIPT
        return script

    def add(self, new_module: IdolModuleType):
        if not (inspect.isclass(new_module)
                and issubclass(new_module, IdolModuleBase)):
            raise ValueError('Invalid Object {}.'.format(repr(new_module)))
        if new_module in self:
            return
        for req in new_module.MODULE_REQUIREMENTS:
            self.add(req)
        print('add module:', new_module.__name__)
        self.modules.append(new_module)
        self.module_identifiers.append(new_module.get_identifier())

    def to_tuple(self) -> Tuple:
        return tuple(self.modules)

    def __contains__(self, item):
        if inspect.isclass(item) and issubclass(item, IdolModuleBase):
            return item.get_identifier() in self.module_identifiers
        elif isinstance(item, str):
            return item in self.module_identifiers
        print(
            'WARNING: IdolModules.__contains__ called with invalid argument {}'.format(
                repr(item)))
        return False
