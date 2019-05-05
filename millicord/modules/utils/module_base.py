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

    async def _void(self, *args, **kwargs):
        pass

    def chain_super(self, name: str, module):
        return getattr(super(module, self), name, self._void)


IdolModuleType = Type[IdolModuleBase]
