import imaplib
import email  #导入两个库
import settings
from utils import print_info

M = imaplib.IMAP4_SSL(host = settings.imap_server)
print('已连接服务器')
M.login(settings.account,settings.password)
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
