import discord
import asyncio
import datetime
import time
import re
import inspect

class IdolClient(discord.Client):
    def __init__(self, idoldata, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idoldata = idoldata
        self.idol_state = None

    #自動ログアウト用のコルーチン
    async def logout_later(self):
        # 時間が来るまで待機
        t =	self.idoldata.leave_at(type_='float') - time.mktime(datetime.datetime.now().timetuple())
        await asyncio.sleep(t)
        await self.logout()

    #ログアウトコルーチンに挨拶を付け加えたもの
    async def logout(self, *args, **kwargs):
        await self.greeting(self.idoldata['actions']['greeting']['lines']["leaving"])
        await super().logout(*args, **kwargs)

    #チャンネル名からチャンネルを取得
    #ないものは弾く
    def get_channels_from_name(self, name):
        ret = []
        for c in self.get_all_channels():
            if c.name == name:
                ret += [c]
        return ret

    #挨拶用のコルーチン
    async def greeting(self, line):
        for gr in self.idoldata["actions"]["greeting"]['rooms']:
            clist = self.get_channels_from_name(gr)
            for c in clist:
                pass
                #await self.send_message(c, line)

   # ログイン時の処理 
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.greeting(self.idoldata['actions']['greeting']["lines"]["attending"])
        #自動ログアウトをセット
        asyncio.ensure_future(self.logout_later())

    # メッセージ受信時の処理
    async def on_message(self, message):
        # ログの取得
        print("In:", message.channel.name)
        print("From: {0}({1})".format(message.author, message.author.id))
        to_list = re.findall("\<@\!?(.+?)\>", message.content)
        print("To:", *to_list)
        print(message.content)

        # botが呼ばれていなければ無視
        if self.user.id not in to_list:
            return
        # 自分の発言なら無視
        if self.user == message.author:
            return

        # 他のタスクをしている場合
        if self.idol_state is not None:
            await self.send_message(message.channel, res["busy"])
        self.idol_state = 'busy'
        # アクション呼び出し
        for k, v in inspect.getmembers(self, predicate=inspect.ismethod):
            print('check', k)
            if re.match('myaction_', k):
                myaction = re.sub('^myaction_', '', k)
                print('try', myaction, self.idoldata.has_action(myaction))
                if self.idoldata.has_action(myaction) and \
                        message.channel.name in self.idoldata['actions'][myaction]['rooms']:
                    res = await getattr(self, k)(message)
                    if res:
                        break
        self.idol_state = None
    # タイムキーパー
    async def myaction_time_keep(self, message):
        to_list = re.findall("\<@\!?(.+?)\>", message.content)
        hour, minute = get_time(message.content)

        if hour == 0 and minute == 0:
            return False
        print("Launch Timekeeper")
        # 時間の取得
        res = self.idoldata['actions']['time_keep']["lines"]
        print(hour, minute)
        member = [message.author.id]
        await self.send_message(message.channel, res["accept"])
        start_time = datetime.datetime.now()
        th = int("{0:%H}".format(start_time))+hour
        tm = int("{0:%M}".format(start_time))+minute
        th = (th+int(tm/60))%24
        tm = tm%60
        await self.send_message(message.channel, res["endtime"].format(hour=th, minute=tm))
        t = hour*3600+minute*60
        await asyncio.sleep(t/2)
        await self.send_message(message.channel, res["notify_half"].format(names=self.pcall(*member)))
        await asyncio.sleep(t/2)
        await self.send_message(message.channel, res["notify_end"].format(names=self.pcall(*member)))

        return True

    def pcall(self, *to_list):
        return "".join(["<@{0}>{1} ".format(uid, self.idoldata["P-call"]) for uid in to_list])

def get_time(s):
	m = re.search("(?P<hour>\d+)時間", s)
	hour, minute = 0, 0
	if m:
		hour = int(m.group("hour")) if m.group("hour") is not None else 0
	m = re.search("(?P<min>\d+)分", s)
	if m:
		minute = int(m.group("min")) if m.group("min") is not None else 0
	return hour, minute
