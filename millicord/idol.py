import yaml
import time
import os
import random
import datetime
from multiprocessing import Process
import sched
from .idol_client import IdolClient
MAX_IDOL_NUM = 5

# timeを今日のdatetimeに
def today_datetime(target_time):
    today = datetime.date.today()
    if isinstance(target_time, str):
        target_time = datetime.datetime.strptime(target_time, "%H:%M:%S").time()
    return datetime.datetime.combine(today, target_time)

# idolの設定ファイル(yaml)を読み込むクラス
# 基本的には辞書と同じようにidol_setting[key]の形で設定を取り出す
class IdolSetting(object):
    def __init__(self, path):
        self.path = path
        self._setting_dict = yaml.load(open(self.path))
        self.token = open(os.path.join(os.path.dirname(path), self["tokenfile"])).read().strip()

    def attend_at(self, type_="datetime"):
        attend_datetime = today_datetime(self["attending_time"])
        if type_ == "datetime":
            return attend_datetime
        elif type_ == "float":
            return time.mktime(attend_datetime.timetuple())

    def leave_at(self, type_="datetime"):
        leaving_datetime = today_datetime(self["leaving_time"])
        if type_ == "datetime":
            return leaving_datetime
        elif type_ == "float":
            return time.mktime(leaving_datetime.timetuple())

    def has_action(self, action):
        return action in self["actions"]

    def __getitem__(self, key):
        return self._setting_dict[key]

    def __str__(self):
        return '{name}({token})'.format(name=self["name"], token=self.token)


#IdolSettingをまとめて管理するクラス
class IdolManager(object):
    def __init__(self):
        self.idols = dict()

    def load_idol(self, path):
        name = os.path.splitext(os.path.split(path)[1])[0]
        self.idols[name] = Idol()
        self.idols[name].set_idoldata(IdolSetting(path))
        print("Add:", str(self.idols[name]))

    def load_from_directory(self, path, names=None):
        for setting in os.listdir(path):
            if os.path.splitext(setting)[1] not in ['.yaml','.yml']:
                continue
            if names is None or idol_name in names:
                self.load_idol(os.path.join(path, setting))

    def select_idols(self):
        idol_num = random.triangular(1, MAX_IDOL_NUM, int(MAX_IDOL_NUM*3/4))
        if idol_num > len(self.idols):
            return self.idols
        else:
            return {k: self.idols[k] for k in random.sample(self.idols.keys(), idol_num)}

    def loop(self):
        pass
        while True:
            idols = self.select_idols()
            schedule = sched.scheduler(time.time, time.sleep)
            priority = 0
            for name, idol in idols.items():
                print(name)
                schedule.enterabs(time=idol.data.attend_at(type_='float'), priority=priority, action=idol.start)
                priority+=1
            t = today_datetime("00:00:00") + datetime.timedelta(days=1)
            t = time.mktime(t.timetuple())
            schedule.enterabs(t, 100000, lambda : print("finish the day"))
            for q in schedule.queue:
                print(q)
            schedule.run()
            for _, idol in idols.items():
                idol.join()

class Idol(Process):
	def run(self):
		# 退勤時刻ならそのままプロセス終了
		if self.data.leave_at() < datetime.datetime.now():
			self.print("too late for attending, end process.")
			return

		# アイドルbotを起動
		self.client = IdolClient(idoldata=self.data)
		self.print("attending {0}".format(self.data.attend_at()))
		self.print("leaving   {0}".format(self.data.leave_at()))
		self.client.run(self.data.token)
		self.print("end process.")

	def print(self, s):
		print("{0}: {1}".format(self.data["name"], s))
	def set_idoldata(self, idoldata):
		self.data = idoldata
