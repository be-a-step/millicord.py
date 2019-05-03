from typing import Type
from discord import Client


class IdolModuleBase(Client):
    MODULE_REQUIREMENTS = [
        # modules required for this module
    ]
    DEFAULT_CONFIG = {
        # key: default_value
    }
    DEFAULT_SCRIPT = {
        # key: default_scripts
    }


IdolModuleType = Type[IdolModuleBase]
