from millicord.utils.module_base import IdolModuleBase
import asyncio
import re
from datetime import datetime, timedelta
from discord import Message
from .basic_module import MessageSenderBaseModule, IdolStateModule, OnMentionedModule


class TimeKeepingModule(IdolModuleBase):
    """TimeKeeperモジュール"""
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        IdolStateModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'accept': 'timekeeping accepted',
        'endtime': 'timer stop at {hour}:{minute}',
        'notify_half': 'time passed half',
        'notify_end': 'timer stop'
    }

    @staticmethod
    def __parse_time(s):
        """
        文字列から時・分を取得

        Parameters
        ----------
        s : str

        Returns
        -------
        delta : timedelta
        """
        m = re.search(r"(?P<hour>\d+)時間", s)
        hours, minutes = 0, 0
        if m:
            hours = int(m.group("hour")) if m.group("hour") is not None else 0
        m = re.search(r"(?P<min>\d+)分", s)
        if m:
            minutes = int(m.group("min")) if m.group("min") is not None else 0
        return timedelta(hours=hours, minutes=minutes)

    async def on_mentioned(self, message: Message):
        """X時間Y分でMentionされた場合にタイマーを起動する"""
        # 各種時刻取得
        delta = self.__parse_time(message.content)
        total_seconds = delta.total_seconds()
        limit = datetime.now() + delta

        # 時間が00:00なら次のコルーチンへ
        if total_seconds == 0:
            c = self.chain_super_coroutine('on_mentioned', TimeKeepingModule)
            await c
            return

        # busy状態へ移行
        self.to_busy()

        async def send_message(key, **kwargs):
            script = self.find_script(TimeKeepingModule, key).format(**kwargs)
            script = self.find_script(TimeKeepingModule, key).format(**kwargs)
            await self.send_message(message.channel, script)

        # 時間の
        await send_message('accept')
        await send_message('endtime', hour=limit.hour, minute=limit.minute)
        await asyncio.sleep(total_seconds / 2)
        await send_message("notify_half")
        await asyncio.sleep(total_seconds / 2)
        await send_message("notify_end")
        self.to_free()
