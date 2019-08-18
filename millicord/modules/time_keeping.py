from millicord.utils.module_base import IdolModuleBase
import asyncio
import re
from datetime import datetime
from discord import Message
from .basic_module import MessageSenderBaseModule, IdolStateModule, OnMentionedModule


def parse_time(s):
    m = re.search(r"(?P<hour>\d+)時間", s)
    hour, minute = 0, 0
    if m:
        hour = int(m.group("hour")) if m.group("hour") is not None else 0
    m = re.search(r"(?P<min>\d+)分", s)
    if m:
        minute = int(m.group("min")) if m.group("min") is not None else 0
    return hour, minute


# タイムキーパー
class TimeKeepingModule(IdolModuleBase):
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

    async def on_mentioned(self, message: Message):
        hour, minute = parse_time(message.content)

        if hour == 0 and minute == 0:
            await self.chain_super_coroutine('on_mentioned', TimeKeepingModule)(message)
            return
        self.to_busy()
        # 時間の取得
        member = [message.author.id]
        await self.send_message(message.channel, self.find_script(TimeKeepingModule, 'accept'))
        start_time = datetime.now()
        th = int("{0:%H}".format(start_time)) + hour
        tm = int("{0:%M}".format(start_time)) + minute
        th = (th + int(tm / 60)) % 24
        tm = tm % 60
        await self.send_message(message.channel, self.find_script(TimeKeepingModule, 'endtime').format(minute=tm, hour=th))
        t = hour * 3600 + minute * 60
        await asyncio.sleep(t / 2)
        await self.send_message(message.channel, self.find_script(TimeKeepingModule, 'notify_half'), )
        await asyncio.sleep(t / 2)
        await self.send_message(message.channel, self.find_script(TimeKeepingModule, 'notify_end'))
        self.to_free()

        return True
