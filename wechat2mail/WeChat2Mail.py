# -*- coding: utf-8 -*-

from wxpy.utils import start_new_thread
import psutil
import datetime
import time
from wxpy import Bot,logging
from queue import Queue
import os,pickle
import zmail
import getpass
## 全局变量区
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="./txtToWeChat.log")
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s')
formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件


bot = Bot(cache_path=True)
black_list = []
process = psutil.Process()
bot.enable_puid(path = "wxpy_puid.pkl")
message_queue = Queue(maxsize= 1000) #保存最近 100 条消息。

MSG_TYPE = {'Text':'文本',
'Map':'位置',
'Card':'名片',
'Note':'提示',
'Sharing':'分享',
'Picture':'图片',
'Recording':'语音',
'Attachment':'文件',
'Video':'视频',
'Friends':'好友请求',
'System':'系统',
}
server = None
mail_id = 0
user_info = {}
## 全局变量区


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






@bot.register()
def process_msg(msg):
    '''
    将消息发送至邮件，如果有文件，则添加附件。
    '''
    type = MSG_TYPE.get(msg.type,"")
    message_text = f"{msg.sender} -> [{type}] - {msg.text}"
    logger.info(message_text)
    message_queue.put(message_text)


def mail_login():
    global server,mail_id,user_info
    user_info = {}
    if os.path.exists("mail_user.pkl"):
        user_info = pickle.load(open("mail_user.pkl", "rb"))
    else:
        mail_address = input("请输入您的邮件地址，如 xxx@163.com：")
        mail_pwd = getpass.getpass("请输入您的邮件登陆密码，此处不回显：")
        user_info = {
            'mail_address':mail_address,
            'mail_pwd':mail_pwd
        }
        pickle.dump(user_info, open("mail_user.pkl", "wb"))
        
    server = zmail.server(
       user_info['mail_address'],user_info['mail_pwd'],
    )

    mail = server.get_latest()
    mail_id = mail["id"] - 1
    logger.debug(f"mail_id: {mail_id}")


def send_mail():
    while True:
        messages = []
        for i in range(10):
            messages.append(message_queue.get())    

        mail_content = {
            'subject': "来自微信的消息",
            'content_text': '\n'.join(messages), # 随便填写
        }

        ##万一发送失败，重试 3 次。
        for i in range(3):
            try:
                server.send_mail(user_info['mail_address'],mail = mail_content)
                print("send to mail success.")
                break
            except:
                mail_login()
    


def send_wechat():
    global server,mail_id
    try:
        mail = server.get_latest()
        max_mail_id = mail["id"]
        logger.debug(f"max_mail_id: {max_mail_id}") 
        while mail_id < max_mail_id:
            mail_id += 1
            logger.info(f" 获取 mail_id 为 {mail_id} 的邮件")
            mail = server.get_mail(mail_id)
            # 主题 + 正文
            content = (
                "".join(mail["content_text"])
                if mail["content_text"] != []
                else "".join(mail["content_html"])
            )
           
            logger.info(f"获取到邮件正文：{content}")
            sender = mail['from']
            logger.debug(sender)
            ##仅处理发件人是自己的邮件
            if user_info['mail_address'] in sender:
                ##想发送给群消息
                logger.debug(mail["subject"])
                if mail["subject"].startswith("group:"):
                    groups = (mail["subject"].replace("group:", "").replace("，", ",")).split(",")
                    for g in groups:
                        group = bot.groups().search(g)
                        if group:
                            group[0].send(content)
                ##发送给朋友
                else:
                    friends = mail["subject"].replace("；", ";").replace(",", ";").replace(" ", ";").split(";")
                    for friend in friends:
                        
                        receiver  = bot.search(friend)
                        if receiver:
                            receiver[0].send(content)
            
        # 删除邮件会导致id>maxid 此时重新定义id为maxid
        if mail_id > max_mail_id:
            mail_id = max_mail_id

    except Exception as e:
        logger.debug(e)
        mail_login()


if __name__ == "__main__":
    mail_login()
    start_new_thread(heartbeat)
    start_new_thread(send_mail)
    while True:
        send_wechat()
        time.sleep(30)
    bot.join()
