from datetime import date, datetime
from typing import Union
from .module_base import IdolModuleType
from .idol_base import IdolBaseType


def get_module_identifier(module: Union[IdolModuleType, IdolBaseType]) -> str:
    return module.__name__


# timeを今日のdatetimeに
def today_datetime(target_time: Union[str, datetime]) -> datetime:
    today = date.today()
    if isinstance(target_time, str):
        target_time = datetime.strptime(target_time, "%H:%M:%S").time()
    return datetime.combine(today, target_time)

