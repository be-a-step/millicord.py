from typing import Type, Callable, Coroutine, TypeVar


class IdolModuleBase:
    """IdolModuleの基底クラス"""
    MODULE_REQUIREMENTS = {
        # modules required for this module
    }
    DEFAULT_CONFIG = {
        # key: default_value
    }
    DEFAULT_SCRIPT = {
        # key: default_scripts
    }

    @classmethod
    def get_identifier(cls) -> str:
        """
        Moduleの識別子を返すクラスメソッド。
        識別子が同じモジュールはbuild時などには同一モジュール扱いとなる。

        Returns
        -------
        module_identifier : str
        """
        return cls.__name__

    async def _void_coroutine(self, *args, **kwargs):
        """Noneを返すコルーチン"""
        return None

    def _void_function(self, *args, **kwargs):
        """Noneを返す関数"""
        return None

    def chain_super_coroutine(self, name, module):
        """
        一つ上のレイヤーのIdolModuleのcoroutineをnameで指定して獲得する。
        存在しない場合にはvoid_coroutineを返す。

        Parameters
        ----------
        name : str
        module : Type[IdolModuleType]

        Returns
        -------
        coro : Callable[Any, Coroutine]
        """
        return getattr(super(module, self), name, self._void_coroutine)

    def chain_super_function(self, name, module):
        """
        一つ上のレイヤーのIdolModuleの関数をnameで指定して獲得する。
        存在しない場合にはvoid_functionを返す。

        Parameters
        ----------
        name : str
        module : Type[IdolModuleBase]

        Returns
        -------
        func : Callable[Any, Any]
        """
        return getattr(super(module, self), name, self._void_function)


IdolModuleType = Type[IdolModuleBase]
