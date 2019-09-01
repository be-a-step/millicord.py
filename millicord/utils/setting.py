import yaml
from pathlib import Path
from collections import UserDict


class YamlBase(UserDict):
    @classmethod
    def load_from_yaml(cls, path):
        """
        yamlファイルから読み込み

        Parameters
        ----------
        path : Union[Path, str]

        Returns
        -------
        self : YamlBase
        """
        with Path(path).open() as f:
            return cls(yaml.load(f, Loader=yaml.FullLoader))

    def write_to_yaml(self, path, default_flow_style=False, overwrite=False):
        """
        yamlファイルへの書き込み。

        Parameters
        ----------
        path : Union[Path, str]
        default_flow_style : bool
            Falseの場合には人が読みやすいように整形される
        overwrite : bool
            上書きフラグ
        """
        mode = "w" if overwrite else "x"
        with Path(path).open(mode) as f:
            s = yaml.dump(self.data, default_flow_style=default_flow_style)
            f.write(s)

    def find_by_path(self, path):
        """
        パス形式でアイテムを探索

        Parameters
        ----------
        path : Union[Path, str]

        Returns
        -------
        item : Any
        """
        tmp = self.data
        for part in Path(path).parts:
            print(part, tmp)
            if part == str(Path('/')):
                continue
            if part not in tmp:
                return None
            tmp = tmp[part]
        return tmp


class IdolConfig(YamlBase):
    pass


class IdolScript(YamlBase):
    pass
