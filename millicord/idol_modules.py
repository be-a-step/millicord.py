import yaml
import sys
from typing import Tuple, List
from millicord.utils.module_base import IdolModuleBase
from pathlib import Path
from millicord.utils.idol_base import IdolBase
from millicord.utils.setting import IdolConfig, IdolScript
from . import modules
import inspect
from collections import Sequence


class IdolModules(Sequence):
    """
    Idolのモジュールコンテナ

    Attributes
    ----------
    modules : List[IdolModuleType]
        モジュールが格納されるリスト
    """

    def __init__(self, *modules):
        self.modules = [IdolBase]
        self.extend(modules)

    @property
    def module_identifiers(self):
        """
        module識別子リスト

        Returns
        -------
        idol_identifiers : List[str]
        """
        return [s.get_identifier() for s in self.modules]

    @classmethod
    def load_from_yaml(cls, path):
        """
        yamlファイルから読み込み

        Parameters
        ----------
        path : Union[Path, str]

        Returns
        -------
        idol_modules : IdolModules

        """
        idol_modules = cls()
        module_dict = yaml.load(Path(path).read_text(), Loader=yaml.FullLoader)
        for module_name in module_dict.get('internal', []):
            if module_name == 'IdolBase':
                continue
            module = getattr(modules, module_name, None)
            if module is None:
                raise ValueError('Unknown module: {}'.format(module_name))
            idol_modules.add(module)
        return idol_modules

    def write_to_yaml(self, path, default_flow_style=False, overwrite=False):
        """
        yamlファイルへ書き込み

        Parameters
        ----------
        path : Union[Path, str]
            書き込み先のパス
        default_flow_style : bool
            Falseなら綺麗に出力
        overwrite : bool
            上書きするかどうか
        """
        path = Path(path)
        if (not overwrite) and path.exists():
            raise FileExistsError(path)
        data = {'internal': self.module_identifiers}
        path.write_text(yaml.dump(data, default_flow_style=default_flow_style))
        # todo: implement external

    def generate_default_config(self) -> IdolConfig:
        """
        初期状態のコンフィグオブジェクトを生成

        Returns
        -------
        config : IdolConfig
        """
        conf = IdolConfig()
        for module in self.modules:
            if len(module.DEFAULT_CONFIG):
                conf[module.get_identifier()] = module.DEFAULT_CONFIG
        return conf

    def generate_default_script(self) -> IdolScript:
        """
        初期状態のスクリプトオブジェクトを生成

        Returns
        -------
        config : IdolScript
        """
        script = IdolScript()
        for module in self.modules:
            if len(module.DEFAULT_SCRIPT):
                script[module.get_identifier()] = module.DEFAULT_SCRIPT
        return script

    def extend(self, modules):
        """
        modulesを一括で追加するメソッド

        Parameters
        ----------
        modules : Iterable[Type[IdolModule]]
        """
        for module in modules:
            self.add(module)

    def add(self, new_module):
        """
        モジュール追加

        Parameters
        ----------
        new_module : Type[IdolModuleBase]
        """
        if not inspect.isclass(new_module) \
           or not issubclass(new_module, IdolModuleBase):
            raise ValueError('Invalid Object {}.'.format(repr(new_module)))
        if new_module in self:
            return
        for req in new_module.MODULE_REQUIREMENTS:
            self.add(req)
        print('add module:', new_module.__name__, file=sys.stderr)
        self.modules.append(new_module)

    def to_tuple(self) -> Tuple:
        return tuple(self.modules)

    def __getitem__(self, key):
        return self.modules[key]

    def __setitem__(self, key):
        raise NotImplementedError("You cannot insert modules. Use add().")

    def __len__(self):
        return len(self.modules)

    def __contains__(self, item):
        if inspect.isclass(item) and issubclass(item, IdolModuleBase):
            return item.get_identifier() in self.module_identifiers
        elif isinstance(item, str):
            return item in self.module_identifiers
        return False
