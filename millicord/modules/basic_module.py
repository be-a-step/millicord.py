from typing import List
import re
from discord import Message
from discord.abc import Messageable
from .utils.module_base import IdolModuleBase


class LoggingModule(IdolModuleBase):
    # ログイン時の処理
    async def on_ready(self):
        print('Logged in as')  # todo: print debug -> logger debug
        print(self.user.name)
        print(self.user.id)
        print('------')
        if hasattr(super(), 'on_ready'):
            await super().on_ready()

    # メッセージ受信時の処理
    async def on_message(self, message: Message):
        # ログの取得
        print("In:", message.channel.name)
        print("From: {0}({1})".format(message.author, message.author.id))
        message_receivers = re.findall("\<@\!?(.+?)\>", message.content)
        print("To:", *message_receivers)
        print(message.content)
        if hasattr(super(), 'on_message'):
            await super().on_message(message)


class MessageSenderBaseModule(IdolModuleBase):
    def mention_formatter(self, message_receivers: list, message_text: str) -> str:
        return " ".join(["<@{0}>".format(uid) for uid in message_receivers] + [message_text])

    async def send_message(self, channel: Messageable, message_text: str, message_receivers: list):
        if len(message_receivers) > 0:
            send_text = self.mention_formatter(message_receivers, message_text)
        else:
            send_text = message_text
        await channel.send(send_text)


class PCallModule(IdolModuleBase):
    MODULE_REQUIREMENTS = [
        MessageSenderBaseModule
    ]
    DEFAULT_CONFIG = {
        'p-call': 'Pさん',
    }

    def mention_formatter(self, message_receivers: list, message_text: str) -> str:
        return " ".join(
            ["<@{0}>{1}".format(uid, self.find_config(PCallModule, "p-call")) for uid in message_receivers] + [message_text]
        )


# メッセージ受信時の処理
class OnMentionedModule(IdolModuleBase):
    async def on_message(self, message: Message):
        message_receiver_ids: List[int] = [int(i) for i in re.findall("\<@\!?(.+?)\>", message.content)]
        # botが呼ばれていたらon_mentionedへ
        if self.user.id in message_receiver_ids:
            await self.on_mentioned(message)
        else:
            if hasattr(super(), 'on_message'):
                await super().on_message(message)

    async def on_mentioned(self, message: Message):
        if hasattr(super(), 'on_mentioned'):
            await super().on_mentioned(message)


class EchoModule(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'message': 'message received'
    }

    async def on_message(self, message: Message):
        if self.user.id == message.author.id:
            return
        await self.send_message(message.channel, self.find_script(EchoModule, 'message'), [])

    async def on_mentioned(self, message: Message):
        if self.user.id == message.author.id:
            return
        await self.send_message(message.channel, self.find_script(EchoModule, 'message'), [message.author.id])
