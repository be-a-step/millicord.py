class IdolSettingError(Exception):
    pass


class IdolBuildError(Exception):
    pass


class IdolScriptError(IdolBuildError):
    pass


class IdolConfigError(IdolBuildError):
    pass


class IdolModuleError(IdolBuildError):
    pass


class IdolBaseError(IdolBuildError):
    pass
