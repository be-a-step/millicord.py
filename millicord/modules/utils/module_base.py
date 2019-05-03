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

    async def chain_coroutine(self, name: str, module, *args, **kwargs):
        await getattr(super(module, self), name, self._void)(*args, **kwargs)

IdolModuleType = Type[IdolModuleBase]
