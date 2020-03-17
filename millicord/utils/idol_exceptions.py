class IdolSettingError(Exception):
    """Idolのconfig/scriptに関連したエラー"""
    pass


class IdolBuildError(Exception):
    """Idolのbuildエラー"""
    pass


class IdolScriptError(IdolBuildError):
    """Idolのscriptの設定項目不足エラー"""
    pass


class IdolConfigError(IdolBuildError):
    """Idolのconfigの設定項目不足エラー"""
    pass


class IdolModuleError(IdolBuildError):
    """Idolのmoduleの依存関係エラー"""
    pass


class IdolBaseError(IdolBuildError):
    """IdolBaseがBuildに使われていないエラー"""
    pass
