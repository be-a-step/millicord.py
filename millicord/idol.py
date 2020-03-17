import os
from typing import Union, List
from pathlib import Path
from shutil import rmtree
from millicord.idol_modules import IdolModules
from millicord.idol_builder import IdolBuilder


#  idol_name/
#   ├ .token
#   ├ config.yaml
#   ├ modules.yaml
#   └ script.yaml
def generate_idol_folder(path, token, module_list, overwrite=False):
    """
    Idolフォルダを生成

    Parameters
    ----------
    path : Union[Path, str]
        生成するフォルダの名前
    token : str
        discord bot のトークン
    module_list : List[IdolModuleType]
        モジュールのリスト
    overwrite : bool
        上書きフラグ

    Returns
    -------
    builder : IdolBuilder
    """

    path = Path(path)
    modules = IdolModules(module_list)
    if overwrite:
        rmtree(path, ignore_errors=True)
    elif path.exists():
        raise FileExistsError(path)

    os.makedirs(path)
    (path / '.token').write_text(token)
    modules.write_to_yaml(path / 'modules.yaml', overwrite=overwrite)
    script = modules.generate_default_script()
    script.write_to_yaml(path / 'script.yaml', overwrite=overwrite)
    config = modules.generate_default_config()
    config.write_to_yaml(path / 'config.yaml', overwrite=overwrite)

    return IdolBuilder(token, path.stem, modules, script, config).build()
