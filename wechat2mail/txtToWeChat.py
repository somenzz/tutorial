# -*- coding: utf-8 -*-
import time
import datetime
from threading import Thread
from wxpy.utils import start_new_thread
import psutil
from wxpy import *
from functools import wraps
from wechat_sender import listen
import subprocess
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="./txtToWeChat.log")
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s')
formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter2)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件


bot = Bot(cache_path=True)
black_list = []
tuling = Tuling()
process = psutil.Process()
org_path = os.getcwd()
bot.enable_puid(path = "wxpy_puid.pkl")


def send_wechat(txtfile):
    if txtfile.split(".")[-1] != "txt":
        return
    file_lines = open(txtfile, "r").readlines()
    if len(file_lines) < 2:
        return
    sen = file_lines[0].strip().split(",")  # 第一行是显示的发件人
    msg = ""
    for s in file_lines[1:]:
        msg += s
    att = file_lines[-1].strip().split(",")  # 第四地是附件目录，支持多个附件,逗号
    send_friends(sen, msg, att)


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
    while bot.alive:
        # noinspection PyBroadException
        try:
            send_iter(bot.self, status_text())
        except:
            logging.exception("failed to report heartbeat:\n")
        time.sleep(3600 * 12)


def send_friends(namelist, msg, filelist=None):
    for name in namelist:
        try:
            receiver = bot.search(name)[0]
            print(receiver)
            receiver.send(msg)
            for f in filelist:
                if f.endswith(".jpg") or f.endswith(".png"):
                    receiver.send_image(f)
                else:
                    receiver.send_file(f)
        except Exception as err:
            print("send_friends error is ", err)


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


@bot.register(Friend)
def save_msg(msg):
    logger.info(msg)

@bot.register(chats=bot.file_helper,msg_types=TEXT,except_self=False)
def wechatController(msg):
    '''
    实现微信控制电脑功能的函数
    :param msg:
    :return:
    '''
    if msg.text in ["help","帮助","怎么用"]:
        return "可发送:\n!截图\n!拍照\n!看目录 路径\n!传文件 文件名\n!关机\n!cmd命令\n!id [10bit]\n!pw<something>"
    if len(msg.text) == 10:
        return get_key(msg.text,new = True)
    if msg.text.startswith("!") or msg.text.startswith("！"):
        command = msg.text.replace("!","").replace("！","")
        if command.startswith("id"):
            return get_key(command.split(" ")[-1],new = False)
        elif command.startswith("pw"):
            return get_key(command,new = True)
        else:
            logger.info(f"将执行命令：{command}")
            if command == "关机":
                process = subprocess.run("shutdown -s -t 0",shell=True,stdout=subprocess.PIPE)
                return process.stdout.decode("gbk")
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

# 响应好友请求
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



if __name__ == "__main__":
    start_new_thread(heartbeat)
    observer = Observer()
    event_handler = FileEventHandler()
    # listen_path=input("请输入要监听的目录（绝对或相对路径）：")
    directory = "D:\share\wechat"
    if len(sys.argv) != 1:
        if os.path.exists(sys.argv[1]):
            directory = sys.argv[1]
        else:
            print("%s is not exists!" % sys.argv[1])
            a = input("press and key to exit()")
            exit(-1)
    logger.info("The monitored directory : " + directory)
    observer.schedule(event_handler, directory, False)
    observer.start()
    # try:
    #     while True:
    #         time.sleep(10)
    # except KeyboardInterrupt:
    #     observer.stop()
    observer.join()
    #listen(bot)
    #embed()
