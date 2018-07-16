import discord
import asyncio
import datetime
import time
import re

class IdolClient(discord.Client):
    def __init__(self, idoldata, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idoldata = idoldata

    async def logout_later(self):
        t =	self.idoldata.leave_at(type_='float') - time.mktime(datetime.datetime.now().timetuple())
        t = 10
        await asyncio.sleep(t)
        await self.logout()

    async def logout(self, *args, **kwargs):
        await self.greeting(self.idoldata['actions']['greeting']['lines']["leaving"])
        await super().logout(*args, **kwargs)

    def get_channels_from_name(self, name):
        ret = []
        for c in self.get_all_channels():
            if c.name == name:
                ret += [c]
        return ret

    async def greeting(self, line):
        for gr in self.idoldata["actions"]["greeting"]['rooms']:
            clist = self.get_channels_from_name(gr)
            for c in clist:
                await self.send_message(c, line)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.greeting(self.idoldata['actions']['greeting']["lines"]["attending"])
        asyncio.ensure_future(self.logout_later())
        #future = asyncio.ensure_future(self.logout_later())
        #self.loop.call_soon(future.done)

    async def on_message(self, message):
        # ログの取得
        print("In:", message.channel.name)
        print("From: {0}({1})".format(message.author, message.author.id))
        to_list = re.findall("\<@\!?(.+?)\>", message.content)
        print("To:", *to_list)
        print(message.content)

        # botが呼ばれていなければ無視
        if self.user == message.author:
            return


        # 他のタスクをしている場合
        if self.idoldata["state"] is not None:
            await self.send_message(message.channel, res["busy"])

        # タイムキーパー
        if self.idoldata.has_action('time_keep'):
            print("Launch Timekeeper")
            if self.user.id in to_list:
                # 時間の取得
                hour, minute = get_time(message.content)
                if hour > 0 or minute > 0:
                    res = self.idoldata['action']['time_keep']["lines"]
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

    def pcall(self, *to_list):
        return "".join(["<@{0}>{1} ".format(uid, self.idoldata["P-call"]) for uid in to_list])
