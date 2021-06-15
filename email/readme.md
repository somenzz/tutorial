## POP3 发送邮件


以下面的代码为例，我们来获取最新的一封邮件内容：
[piplib_demo.py](./poplib_demo.py)

```python
import poplib
from email.parser import Parser
from utils import print_info
import settings


# 连接到POP3服务器:
server = poplib.POP3(settings.pop3_server)
# 身份认证:
server.user(settings.email)
server.pass_(settings.password)

# stat()返回邮件数量和占用空间:
print('Messages: %s. Size: %s' % server.stat())
# list()返回所有邮件的编号:
resp, mails, octets = server.list()
# 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]

# 获取最新一封邮件, 注意索引号从1开始:
latest_mail_index = len(mails)
resp, lines, octets = server.retr(latest_mail_index)

# lines存储了邮件的原始文本的每一行,
# 可以获得整个邮件的原始文本:
msg_content = b'\r\n'.join(lines).decode('utf-8')
# 稍后解析出邮件:
msg = Parser().parsestr(msg_content)
print_info(msg)
# 邮件索引号直接从服务器删除邮件
# server.dele(index)
# 关闭连接:
server.quit()
```

poplib 收取邮件分两步：第一步是获取邮件列表，第二步是用 email 模块把原始邮件解析为 Message 对象，然后，用适当的形式把邮件内容展示出来。

## 基于 poplib 的三方库

使用完标准库 poplib，我只想说，还是三方库用起来爽。

#### zmail

Zmail 使得在 Python3 中发送和接受邮件变得更简单。你不需要手动添加服务器地址、端口以及适合的协议，zmail 会帮你完成。此外，使用一个字典来代表邮件内容也更符合直觉。

Zmail 仅支持 Python3，不依赖任何三方库。安装方法：

```sh
pip install zmail
```

特性：

- 自动寻找服务器地址以及端口
- 自动使用可靠的链接协议
- 自动将一个python字典映射成MIME对象（带有附件的）
- 自动添加头文件以及localhostname来避免服务器拒收你的邮件
- 轻松自定义你的头文件
- 支持使用HTML作为邮件内容
- 仅需 python>=3.5，你可以将其嵌入你的项目而无需其他的依赖

示例代码：

```python
import zmail
server = zmail.server('yourmail@example.com', 'yourpassword')

# Send mail
server.send_mail('yourfriend@example.com',{'subject':'Hello!','content_text':'By zmail.'})
# Or to a list of friends.
server.send_mail(['friend1@example.com','friend2@example.com'],{'subject':'Hello!','content_text':'By zmail.'})

# Retrieve mail
latest_mail = server.get_latest()
zmail.show(latest_mail)
```

可以看出，接收最新的邮件只需要两行代码：

```python
latest_mail = server.get_latest()
zmail.show(latest_mail)
```
很是好用。


文档：https://github.com/zhangyunhao116/zmail/blob/master/README-cn.md



## imap 接收邮件

很多主流邮箱如 163，qq 邮箱默认关闭了 imap 的服务，可手动前往邮箱账户设置页面开启，并生成授权码，授权码就是代码中用于登录的密码。

获取最新的邮件并展示：

[imap_demo.py](./imaplib_demo.py)

```python
import imaplib
import email  #导入两个库
import settings
from utils import print_info

M = imaplib.IMAP4_SSL(host = settings.imap_server)
print('已连接服务器')
M.login(settings.email,settings.password)
print('已登陆')
print(M.noop())
M.select()

typ, data = M.search(None, 'ALL')
for num in data[0].split():
    typ, data = M.fetch(num, '(RFC822)')
    # print('Message %s\n%s\n' % (num, data[0][1]))
    # print(data[0][1].decode('utf-8'))
    msg = email.message_from_string(data[0][1].decode('utf-8'))
    print_info(msg)
    break
M.close()
M.logout()

```

## 基于 imaplib 的三方库

你可能会问：为什么要为 Python 创建另一个 IMAP 客户端库？Python 标准库不是已经有 imaplib 了吗？。

imaplib 的问题在于它非常底层。 使用起来相当复杂，你可能需要处理很多细节问题，由于 IMAP 服务器响应可能非常复杂，这意味着使用 imaplib 的每个人最终都会编写自己的脆弱解析程序。

此外，imaplib 没有很好地利用异常。 这意味着您需要检查 imaplib 的每次调用的返回值，以查看请求是否成功。


#### imapclient

imapclient 在内部使用的 imaplib，但比 imaplib 好用的多，示例代码如下：

[imapclient_demo.py](./imapclient_demo.py)
```python
import ssl
from imapclient import IMAPClient
import settings
# context manager ensures the session is cleaned up


ssl_context = ssl.create_default_context()
# don't check if certificate hostname doesn't match target hostname
ssl_context.check_hostname = False
# don't check if the certificate is trusted by a certificate authority
ssl_context.verify_mode = ssl.CERT_NONE

with IMAPClient(host=settings.imap_server,ssl_context=ssl_context) as client:
    client.login(settings.account,settings.password)
    select_info = client.select_folder('INBOX')
    print('%d messages in INBOX' % select_info[b'EXISTS'])
    # search criteria are passed in a straightforward way
    # (nesting is supported)
    messages = client.search(['FROM', 'xxxx@163.com'])
    # `response` is keyed by message id and contains parsed,
    # converted response items.
    for message_id, data in client.fetch(messages, ['ENVELOPE']).items():
        envelope = data[b'ENVELOPE']
        print('{id}: subject: {subject} date: {date}'.format(
            id=message_id,
            subject = envelope.subject.decode(),
            date = envelope.date
        ))
```

文档： https://github.com/mjs/imapclient


#### imap_tools

通过 IMAP 处理电子邮件和邮箱，支持以下功能：

- 解析的电子邮件消息属性
- 用于搜索电子邮件的查询生成器
- 使用电子邮件的操作：复制、删除、标记、移动、看到、追加
- 使用文件夹的操作：列表、设置、获取、创建、存在、重命名、删除、状态
- 没有依赖项

```python
pip install imap-tools
```

示例代码：

```python
from imap_tools import MailBox, AND

# get list of email subjects from INBOX folder
with MailBox('imap.mail.com').login('test@mail.com', 'pwd') as mailbox:
    subjects = [msg.subject for msg in mailbox.fetch()]

# get list of email subjects from INBOX folder - equivalent verbose version
mailbox = MailBox('imap.mail.com')
mailbox.login('test@mail.com', 'pwd', initial_folder='INBOX')  # or mailbox.folder.set instead 3d arg
subjects = [msg.subject for msg in mailbox.fetch(AND(all=True))]
mailbox.logout()
```


文档：https://github.com/ikvk/imap_tools
