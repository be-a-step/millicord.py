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

    async def _void_coroutine(self, *args, **kwargs):
        return args, kwargs

    def _void_function(self, *args, **kwargs):
        return args, kwargs

    def chain_super_coroutine(self, name: str, module):
        return getattr(super(module, self), name, self._void_coroutine)

    def chain_super_function(self, name: str, module):
        return getattr(super(module, self), name, self._void_function)


IdolModuleType = Type[IdolModuleBase]
