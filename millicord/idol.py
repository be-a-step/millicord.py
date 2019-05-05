import os
from typing import Union, List
from pathlib import Path
from shutil import rmtree
from .idol_modules import IdolModules
from .modules.utils.module_base import IdolModuleBase, IdolModuleType
from .idol_builder import IdolBuilder


#  idol_name/
#   ├ .token
#   ├ config.yaml
#   ├ modules.yaml
#   └ script.yaml
def generate_idol_folder(path: Union[Path,
                                     str],
                         token: str,
                         module_list: List[IdolModuleType],
                         overwrite: bool = False):
    path = Path(path)
    if (not overwrite) and path.exists():
        raise FileExistsError(path)

    modules = IdolModules()
    for module in module_list:
        if not issubclass(module, IdolModuleBase):
            raise ValueError('{} is not IdolModule'.format(repr(module)))
        modules.add(module)

    if overwrite:
        rmtree(path, ignore_errors=True)

    os.makedirs(path)
    with (path / '.token').open('w') as f:
        f.write(token)
    modules.write_to_yaml(path / 'modules.yaml', overwrite=overwrite)
    script = modules.generate_default_script()
    script.write_to_yaml(path / 'script.yaml', overwrite=overwrite)
    config = modules.generate_default_config()
    config.write_to_yaml(path / 'config.yaml', overwrite=overwrite)

    return IdolBuilder(
        token=token,
        name=path.stem,
        modules=modules,
        config=config,
        script=script
    ).build()
