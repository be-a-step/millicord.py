from random import choice
from typing import List, Optional, Union
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
        await self.chain_super('on_ready', LoggingModule)()

    # メッセージ受信時の処理
    async def on_message(self, message: Message):
        # ログの取得
        print("In:", message.channel.name)
        print("From: {0}({1})".format(message.author, message.author.id))
        message_receivers = re.findall(r"\<@\!?(.+?)\>", message.content)
        print("To:", *message_receivers)
        print(message.content)
        await self.chain_super('on_message', LoggingModule)(message)

    # async def on_mentioned(self, message: Message):
    #     await self.chain_super('on_mentioned', LoggingModule)(message)


class MessageSenderBaseModule(IdolModuleBase):
    def mention_formatter(
            self, message_receivers: List[Union[int, str]], message_text: str) -> str:
        return " ".join(["<@{0}>".format(uid)
                         for uid in message_receivers] + [message_text])

    async def send_message(self, channel: Messageable, message_text: str, message_receivers: Union[list, str, int, None] = None):
        if message_receivers is None:
            send_text = message_text
        elif isinstance(message_receivers, (int, str)):
            send_text = self.mention_formatter(
                [message_receivers], message_text)
        elif isinstance(message_receivers, list) and len(message_receivers) > 0:
            send_text = self.mention_formatter(message_receivers, message_text)
        else:
            raise ValueError(
                'Invalid message receivers passed: {}'.format(message_receivers))
        await channel.send(send_text)
        await self.chain_super('send_message', MessageSenderBaseModule)(channel, message_text, message_receivers)


class PCallModule(IdolModuleBase):
    MODULE_REQUIREMENTS = [
        MessageSenderBaseModule
    ]
    DEFAULT_CONFIG = {
        'p-call': 'Pさん',
    }

    def mention_formatter(
            self,
            message_receivers: list,
            message_text: str) -> str:
        return " ".join(["<@{0}>{1}".format(uid, self.find_config(
            PCallModule, "p-call")) for uid in message_receivers] + [message_text])


# メッセージ受信時の処理
class OnMentionedModule(IdolModuleBase):
    async def on_message(self, message: Message):
        # botが呼ばれていたらon_mentionedへ
        if str(self.user.id) in re.findall(r"\<@\!?(.+?)\>", message.content):
            await self.chain_super('on_mentioned', OnMentionedModule)(message)
        else:
            await self.chain_super('on_message', OnMentionedModule)(message)


class EchoModule(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        # MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'message': 'message received'
    }

    async def on_message(self, message: Message):
        if self.user.id == message.author.id:
            return
        await self.send_message(message.channel, self.find_script(EchoModule, 'message'))

    async def on_mentioned(self, message: Message):
        if self.user.id == message.author.id:
            return
        await self.send_message(message.channel, self.find_script(EchoModule, 'message'), message.author.id)


STATE_FREE = 0
STATE_BUSY = 1


class IdolStateModule(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'busy_apologize': "I'm busy and cannot respond."
    }

    def __init__(self, *args, **kwargs):
        if hasattr(super(), '__init__'):
            super().__init__(*args, **kwargs)
        self.state = STATE_FREE

    def is_busy(self):
        return self.state == STATE_BUSY

    def to_busy(self):
        self.state = STATE_BUSY

    def to_free(self):
        self.state = STATE_FREE

    async def on_message(self, message: Message):
        if self.is_busy():
            pass
        else:
            await self.chain_super('on_message', IdolStateModule)(message)

    async def on_mentioned(self, message: Message):
        if self.is_busy():
            await self.send_message(message.channel, self.find_script(IdolStateModule, 'busy_apologize'), message.author.id)
        else:
            await self.chain_super('on_mentioned', IdolStateModule)(message)


class RandomResposeModule(IdolModuleBase):
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'message_1': "Hi!",
        'message_2': "What's up?",
        'message_3': "Hello"
    }

    async def on_mentioned(self, message: Message):
        sampled_message = choice(
            list(
                self.find_script(
                    RandomResposeModule,
                    '').values()))
        await self.send_message(message.channel, sampled_message, message.author.id)
