# -*- coding: utf-8 -*-
import time,os
import datetime
from wxpy.utils import start_new_thread
import psutil
from wxpy import *
from functools import wraps
import cv2
#可用于监控你的程序
#from wechat_sender import listen

import subprocess
org_path = os.getcwd()
###记录日志信息
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="info.log")
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件

###定义全局变量
bot = Bot(cache_path=True)
black_list = []
tuling = Tuling()
process = psutil.Process()

# 在 Web 微信中把自己加为好友
try:
    bot.self.add()
    bot.self.accept()
except:
    pass

###定义功能函数
def _status_text():
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(
        process.create_time()
    )
    memory_usage = process.memory_info().rss

    if globals().get("bot"):
        messages = bot.messages
    else:
        messages = list()

    return "[now] {now:%H:%M:%S}\n[uptime] {uptime}\n[memory] {memory}\n[messages] {messages}".format(
        now=datetime.datetime.now(),
        uptime=str(uptime).split(".")[0],
        memory="{:.2f} MB".format(memory_usage / 1024 ** 2),
        messages=len(messages),
    )

0

def status_text():
    yield _status_text()


def send_iter(receiver, iterable):
    """
    用迭代的方式发送多条消息

    :param receiver: 接收者
    :param iterable: 可迭代对象
    """

    if isinstance(iterable, str):
        raise TypeError

    for msg in iterable:
        receiver.send(msg)


def heartbeat():
    '''
    每 12 小时向文件传输助手报告一下本程序运行状态
    '''
    while bot.alive:
        # noinspection PyBroadException
        try:
            send_iter(bot.self, status_text())
        except:
            logging.exception("failed to report heartbeat:\n")
        time.sleep(3600 * 12)



# 限制频率: 指定周期内超过消息条数，直接回复 "🙊"
def freq_limit(period_secs=15, limit_msgs=5):
    def decorator(func):
        @wraps(func)
        def wrapped(msg):
            if msg.chat in black_list:
                return
            now = datetime.datetime.now()
            period = datetime.timedelta(seconds=period_secs)
            recent_received = 0
            for m in msg.bot.messages[::-1]:
                if m.sender == msg.sender:
                    if now - m.create_time > period:
                        break
                    recent_received += 1
            if recent_received > 8:
                black_list.append(msg.chat)
                return "你说得好快，我都累了，休息一下吧"
            elif recent_received > limit_msgs:
                if not isinstance(msg.chat, Group) or msg.is_at:
                    return "🙊"
            return func(msg)
        return wrapped
    return decorator

@bot.register(bot.self,except_self= False)
def chat_to_self(msg):
    '''
    自己和自己聊天
    :param msg:
    :return:
    '''
    tuling.do_reply(msg)

@bot.register(Friend)
def save_msg(msg):
    '''
    记录好友发送的所有消息，防止消息被撤回，保存在日志文件中
    :param msg:
    :return:
    '''
    logger.info(msg)



# 自动响应好友添加请求
@bot.register(msg_types=FRIENDS)
def new_friend(msg):
    if msg.card in black_list:
        return
    user = msg.card.accept()
    user.set_remark_name(msg.text.replace("我是","").replace('我','').replace(' ',''))
    # if valid(msg):
    #    invite(user)


# 手动加为好友后自动发送消息
@bot.register(Friend, NOTE)
def manually_added(msg):
    if "现在可以开始聊天了" in msg.text:
        # 对于好友验证信息为 wxpy 的，会等待邀请完成 (并计入 invite_counter)
        # 对于好友验证信息不为 wxpy 的，延迟发送更容易引起注意
        time.sleep(3)
        return "你好呀，{}".format(msg.chat.name)

@bot.register(chats=bot.file_helper,msg_types=TEXT,except_self=False)
def wechatController(msg):
    '''
    实现微信控制电脑功能的函数
    :param msg:
    :return:
    '''
    if msg.text in ["help","帮助","怎么用"]:
        return "可发送:\n!截图\n!拍照\n!看目录 路径\n!传文件 文件名\n!关机\n!cmd命令"
    if msg.text.startswith("!") or msg.text.startswith("！"):
        command = msg.text.replace("!","").replace("！","")
        logger.info(f"将执行命令：{command}")
        if command == "关机":
            process = subprocess.run("shutdown -s -t 0",shell=True,stdout=subprocess.PIPE)
            return process.stdout.decode("gbk")
        elif command == "拍照":
            os.chdir(org_path)
            cap = cv2.VideoCapture(0)
            ret, img = cap.read()
            cv2.imwrite("capture.jpg", img)
            cap.release()
            bot.file_helper.send_image("capture.jpg")
        elif command == "截图":
            os.chdir(org_path)
            process = subprocess.run("nircmd savescreenshot capture_screen.png",shell=True,stdout=subprocess.PIPE)
            bot.file_helper.send_image("capture_screen.png")
            return process.stdout.decode("gbk")
        elif command.startswith("看目录"):
            dir = ""
            dir = command.replace("看目录","")
            print(dir)
            if dir != "":
                os.chdir(dir)
                process = subprocess.run("dir", shell=True,stdout=subprocess.PIPE)
                return process.stdout.decode("gbk")

        elif command.startswith("传文件"):
            file_name = ""
            file_name = command.replace("传文件","")
            if file_name != "":
                if file_name.endswith(".png") or file_name.endswith(".jpg"):
                    bot.file_helper.send_image(file_name)
                else:
                    bot.file_helper.send_file(file_name)
        else:
            os.chdir(org_path)
            process = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
            return process.stdout.decode("gbk")



###主程序入口
# if __name__ == '__main__':
def main():
    start_new_thread(heartbeat)
    bot.join()
    # embed()
