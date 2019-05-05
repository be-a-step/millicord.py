import yaml
from typing import Union, NewType
from pathlib import Path
from collections import UserDict
from datetime import datetime

YamlItemType = NewType('YamlItemType',
                       Union[str,
                             int,
                             float,
                             bool,
                             None,
                             dict,
                             datetime,
                             bytes,
                             set,
                             list])
IdolConfigItemType = NewType('IdolConfigItemType', YamlItemType)
IdolScriptItemType = NewType('IdolScriptItemType', str)


class YamlBase(UserDict):
    @classmethod
    def load_from_yaml(cls, path: Union[Path, str]):
        with Path(path).open() as f:
            return cls(yaml.load(f, Loader=yaml.FullLoader))

    def write_to_yaml(self,
                      path: Union[Path,
                                  str],
                      default_flow_style=False,
                      overwrite=False):
        path = Path(path)
        if (not overwrite) and path.exists():
            raise FileExistsError(path)
        with path.open('w') as f:
            f.write(
                yaml.dump(
                    self.data,
                    default_flow_style=default_flow_style))

    def find_by_path(self, path: Union[Path, str]) -> YamlItemType:
        tmp = self.data
        for part in Path(path).parts:
            print(part, tmp)
            if part == '/':
                continue
            if part not in tmp:
                return None
            tmp = tmp[part]
        return tmp


class IdolConfig(YamlBase):
    def find_by_path(self, path: Union[Path, str]) -> IdolConfigItemType:
        return super().find_by_path(path)


class IdolScript(YamlBase):
    def find_by_path(self, path: Union[Path, str]) -> IdolScriptItemType:
        return super().find_by_path(path)


IdolConfigType = NewType('IdolConfigType', IdolConfig)
IdolScriptType = NewType('IdolScriptType', IdolScript)
