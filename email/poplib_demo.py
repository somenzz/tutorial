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
# print(mails)

# 获取最新一封邮件, 注意索引号从1开始:
latest_mail_index = len(mails)
resp, lines, octets = server.retr(latest_mail_index)

# lines存储了邮件的原始文本的每一行,
# 可以获得整个邮件的原始文本:
msg_content = b'\r\n'.join(lines).decode('utf-8')
# 稍后解析出邮件:
msg = Parser().parsestr(msg_content)
print_info(msg)
# 可以根据邮件索引号直接从服务器删除邮件:print
# server.dele(index)
# 关闭连接:
server.quit()