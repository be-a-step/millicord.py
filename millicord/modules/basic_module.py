from random import choice
from typing import List
import re
from discord import Message
from millicord.utils.module_base import IdolModuleBase


# todo: ロギングを各モジュールに移譲して消す
class LoggingModule(IdolModuleBase):
    # ログイン時の処理
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.chain_super_coroutine('on_ready', LoggingModule)()

    # メッセージ受信時の処理
    async def on_message(self, message: Message):
        # ログの取得
        print("In:", message.channel.name)
        print("From: {0}({1})".format(message.author, message.author.id))
        to_ids = re.findall(r"\<@\!?(.+?)\>", message.content)
        print("To:", *to_ids)
        print(message.content)
        await self.chain_super_coroutine('on_message', LoggingModule)(message)


class MessageSenderBaseModule(IdolModuleBase):
    """メッセージを送信するモジュールの前提モジュール"""

    def mention_formatter(self, to_ids, message_text):
        """
        メンションのフォーマッタ

        Parameters
        ----------
        to_ids : List[Union[int, str]]
            mention先userのidリスト
        message_text : str
            メッセージ

        Returns
        -------
        formatted_text : str

        """
        uid_text = ["<@{0}>".format(uid) for uid in to_ids]
        formatted_text = " ".join(uid_text + [message_text])
        sf = self.chain_super_function(
            'mention_formatter', MessageSenderBaseModule)
        return sf(to_ids, formatted_text) or formatted_text

    async def send_message(self, channel, message_text, to_ids=None):
        """
        メッセージ送信コルーチン

        Parameters
        ----------
        channel : discord.abc.Messageable
            対象のチャンネル
        message_text : str
            messageの本文
        to_ids : Optional[list, str, int]
            mention先userのidリスト
        """
        if to_ids is None:
            send_text = message_text
        elif isinstance(to_ids, (int, str)):
            send_text = self.mention_formatter(
                [to_ids], message_text)
        elif isinstance(to_ids, list) and len(to_ids) > 0:
            send_text = self.mention_formatter(to_ids, message_text)
        else:
            raise ValueError(f'Invalid message receivers: {to_ids}')
        await channel.send(send_text)
        c = self.chain_super_coroutine('send_message', MessageSenderBaseModule)
        await c(channel, message_text, to_ids)


class PCallModule(IdolModuleBase):
    """メンション先のIDに接尾辞を付けるコルーチン"""
    MODULE_REQUIREMENTS = [
        MessageSenderBaseModule
    ]
    DEFAULT_CONFIG = {
        'p-call': 'Pさん',
    }

    def mention_formatter(self, to_ids, message_text):
        """
        メンション先のIDに接尾辞を付けるコルーチン
        e.g. "@hoge" -> "@hoge Pさん"

        Parameters
        ----------
        to_ids : List[Union[int, str]]
            mention先userのidリスト
        message_text : str
            メッセージ

        Returns
        -------
        formatted_text : str

        """
        sfx = self.find_config(PCallModule, "p-call")
        formatted_text = re.sub(r"(<@\d+>)", r"\1" + sfx, message_text)
        sf = self.chain_super_function(
            'mention_formatter', PCallModule)
        return sf(to_ids, formatted_text) or formatted_text


# メッセージ受信時の処理
class OnMentionedModule(IdolModuleBase):
    """on_mentionedの前提モジュール"""
    async def on_message(self, message):
        """
        on_messageの呼び出しのうちmentionをon_mentionedへと分岐させるコルーチン。

        Parameters
        ----------
        message : Message
        """
        if str(self.user.id) in re.findall(r"\<@\!?(.+?)\>", message.content):
            sc = self.chain_super_coroutine('on_mentioned', OnMentionedModule)
            await sc(message)
        else:
            sc = self.chain_super_coroutine('on_message', OnMentionedModule)
            await sc(message)


class EchoModule(IdolModuleBase):
    """メッセージが送られるたびに固定メッセージを返すモジュール"""
    MODULE_REQUIREMENTS = {
        # MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'message': 'message received'
    }

    async def on_message(self, message: Message):
        """
        messageにmessageを返すコルーチン

        Parameters
        ----------
        message : Message
        """
        if self.user.id == message.author.id:
            return
        script = self.find_script(EchoModule, 'message')
        await self.send_message(message.channel, script)

    async def on_mentioned(self, message: Message):
        """
        mentionにmentionを返すコルーチン

        Parameters
        ----------
        message : Message
        """
        if self.user.id == message.author.id:
            return
        script = self.find_script(EchoModule, 'message')
        await self.send_message(message.channel, script, message.author.id)


STATE_FREE = 0
STATE_BUSY = 1


class IdolStateModule(IdolModuleBase):
    """アイドルにbusy状態を導入するモジュール"""
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'busy_apologize': "I'm busy and cannot respond."
    }

    def __init__(self):
        self.chain_super_function("__init__", IdolStateModule)()
        self.state = STATE_FREE

    def is_busy(self):
        """stateがbusyなのかを判定するメソッド"""
        return self.state == STATE_BUSY

    def to_busy(self):
        """stateをbusyに切り替えるメソッド"""
        self.state = STATE_BUSY

    def to_free(self):
        """stateをfreeに切り替えるメソッド"""
        self.state = STATE_FREE

    async def on_message(self, message):
        """
        busyならメッセージを無視するようにするコルーチン

        Parameters
        ----------
        message : Message
        """
        if self.is_busy():
            return
        sc = self.chain_super_coroutine('on_message', IdolStateModule)
        await sc(message)

    async def on_mentioned(self, message: Message):
        """
        mentionを受けたとき、busyなら謝って断るモジュール

        Parameters
        ----------
        message : Message
        """
        if self.is_busy():
            script = self.find_script(IdolStateModule, 'busy_apologize')
            await self.send_message(message.channel, script, message.author.id)
            return
        sc = self.chain_super_coroutine('on_mentioned', IdolStateModule)
        await sc(message)


class RandomResposeModule(IdolModuleBase):
    """ランダムなメッセージを返すモジュール"""
    MODULE_REQUIREMENTS = {
        MessageSenderBaseModule,
        OnMentionedModule
    }
    DEFAULT_SCRIPT = {
        'message_1': "Hi!",
        'message_2': "What's up?",
        'message_3': "Hello"
    }

    async def on_mentioned(self, message):
        """
        mentionを受けたとき、ランダムに返答するコルーチン

        Parameters
        ----------
        message : Message
        """
        scripts = list(self.find_script(RandomResposeModule, '').values())
        script = choice(scripts)
        await self.send_message(message.channel, script, message.author.id)
