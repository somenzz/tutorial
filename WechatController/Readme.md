# Python实战-让微信遥控你的电脑

学习 Python 最好的方法，就是使用它，使用它来解决问题，这种正向激励会让你坚持不断的深入研究，进而在 Python 的道路上投入一万小时，从而成为 Python 大师。这里再宣传下一万小时定律：

>“人们眼中的天才之所以卓越非凡，并非天资超人一等，而是付出了持续不断的努力。1万小时的锤炼是任何人从平凡变成世界级大师的必要条件。”他将此称为“一万小时定律”。

现在都是快节奏的办公生活，大家都是同时使用手机和电脑，这就免不了使用微信与电脑之间相互传递文件，想一想你使用过多少次文件传输助手？

当你在电脑前时，手机与电脑之间相互传文件都非常简单。当你不在电脑前呢？ 比如你正在开会，突然有个紧急电话让你把xx文件发给xx；正在会议室讨论需求，却想看下电脑中的一个文件；或者正在外面吃饭，想看下电脑上跑的程序运行完没有，想到电脑还没有关机，想让它关机。

解决这些问题，使用 Python 的话，只需要通过一个 wxpy 模块就可以轻松实现，小白也完全可以自已定制，非常方便。话不多说，先看个视频。

视频演示：使用手机上的【文件传输助手】来控制【登陆微信网页版】的电脑。

[https://zhuanlan.zhihu.com/p/87214896](https://zhuanlan.zhihu.com/p/87214896)

原理非常简单，就是使用手机发送消息到网页版微信，网页版微信收到消息后执行相应的任务，然后把结果返回给手机端，由于网页版微信在电脑端登陆，因此可以控制电脑。

这个逻辑同样适用于邮件，或者其他可以编程控制的通讯工具，由于微信的使用率最高，也最方便，因此这里选取微信做为样例。


#### 使用到的工具 wxpy

官方链接: https://github.com/youfou/wxpy

wxpy 是一个第三方库，我们叫它微信机器人，是最优雅的微信个人号 API。说的简单点，就是一个微信网页版的爬虫，你也可以自己实现这样的库。

使用这个工具可以干吗？

- 控制路由器、智能家居等具有开放接口的玩意儿
- 运行脚本时自动把日志发送到你的微信
- 加群主为好友，自动拉进群中
- 跨号或跨群转发消息
- 自动陪人聊天
- 逗人玩

注意如里发消息太频繁会被限制网页版微信登陆，所以还是不要玩的太过分，不要发送大量无用的信息去干扰他人，我正常使用了 2 年了，主要发一些定时提醒消息，传少量文件，至今还可以正常登陆。

安装方法：

```python
pip install wxpy
```

#### 核心代码

当机器人文件传输助手收到文本消息时，判断是否是 ！开头，如果是，则执行相应的任务并返回响应信息。

```python

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
            dir = ""
            dir = command.replace("传文件","")
            if dir != "":
                bot.file_helper.send_file(dir)

        else:
            os.chdir(org_path)
            process = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
            return process.stdout.decode("gbk")

```

代码还有一些其他功能函数，比如你可以和自己聊天，记录所有收到的消息到日志，防止撤回，监控程序使用的内存等信息，参考 wxpy 的文档来定制你的需求吧。

```python

@bot.register(bot.self,except_self= False)
def chat_to_self(msg):
    '''
    自己和自己聊天
    :param msg:
    :return:
    '''
    Tuling.do_reply(msg)

@bot.register(Friend)
def save_msg(msg):
    '''
    记录好友发送的所有消息，防止消息被撤回，保存在日志文件中
    :param msg:
    :return:
    '''
    logger.info(msg)

```

完整代码及一键可执行的文件，我已生成好，放在百度云盘中，关注公众号 Python七号 ，后台回复关键词 [微信遥控] 获取。


无论何时何地，希望您能自由随心访问和管理您的电脑。

