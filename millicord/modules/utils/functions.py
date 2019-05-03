from datetime import date, datetime
from typing import Union, Type

# 引数のtypingは本来 module: Union[IdolModuleType, IdolBaseType] と書くべきだけど、循環参照が起きるのでひとまずこうしておく
def get_module_identifier(module: Type) -> str:
    return module.__name__


# timeを今日のdatetimeに
def today_datetime(target_time: Union[str, datetime]) -> datetime:
    today = date.today()
    if isinstance(target_time, str):
        target_time = datetime.strptime(target_time, "%H:%M:%S").time()
    return datetime.combine(today, target_time)
