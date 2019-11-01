#!/home/aaron/pyenv/bin/python3
# encoding=utf-8

from wechat_sender import Sender
import zmail
import time
import logging
import threading

# 构造接收者字典
import settings


logger0 = logging.getLogger("zmail")
logger0.setLevel(logging.ERROR)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="./mailToWeChat.log")
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s"
)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件


server = zmail.server(
    settings.mail_user, settings.mail_pwd, pop_host=settings.mail_host
)
mail = server.get_latest()
id = mail["id"] - 1
logger.info(f" 登陆成功，获取到最新邮件编号 { id }\n")
sender = Sender()


def get_mail_to_wechat():
    global id, server, sender
    try:
        mail = server.get_latest()
        maxid = mail["id"]

        while id < maxid:
            id += 1
            logger.info(f" 获取 id 为 {id} 的邮件")
            mail = server.get_mail(id)
            # 主题 + 正文
            content = (
                "".join(mail["content"])
                if mail["content"] != []
                else "".join(mail["content_html"])
            )
            message = f"""主题：\n{mail['subject']}\n正文：\n{content}"""
            logger.info(message)
            send_ip = mail["raw"][17].decode("utf-8").split(":")[1].replace(" ", "")
            # logger.info(type(send_ip))
            logger.info(f" from {send_ip}")
            # 来自指定IP发送的邮件才发送微信
            if send_ip in settings.ip:
                # 逐个发送微信
                logger.info(f": 来自 {send_ip}，发消息至以朋友")
                print(mail["to"])
                for index in mail["to"].replace(",", ";").split(";"):
                    print(index)
                    friends = (
                        settings.receiver.get(index.replace(" ", ""), "清如許")
                    ).split(",")
                    logger.info(friends)
                    for friend in friends:
                        while True:
                            try:
                                re = sender.send_to(content=message, search=friend)
                                if re[0]:
                                    break
                            except:
                                pass

                        # if friend == "清如許":
                        #    re = sender.send(message)
                        #    logger.info(re)
                        # else:
                        #    re = sender.send_to(content=message, search=friend)
                        #    logger.info(re)
                # 向群组发送微信
                if mail["subject"].startswith("group:"):
                    groups = (mail["subject"].replace("group:", "")).split(",")
                    for g in groups:
                        while True:
                            try:
                                re = sender.send_to(
                                    content=f"打扰了，这是一条告警信息，请关注\n{content}", search=g
                                )
                                if re[0]:
                                    break
                            except:
                                pass

        # 删除邮件会导致id>maxid 此时重新定义id为maxid
        if id > maxid:
            id = maxid

    except Exception as e:
        logger.info(f": send err is [{e}] \n开始重新登陆邮箱")
        server = zmail.server(
            settings.mail_user, settings.mail_pwd, pop_host=settings.mail_host
        )
        logger.info(f" 登陆成功，获取到最新邮件编号 { id }\n")
        sender = Sender()


if __name__ == "__main__":
    while True:
        task = threading.Thread(target=get_mail_to_wechat, args=())
        task.start()
        task.join(timeout=120)
        time.sleep(40)
