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
    messages = client.search(['FROM', 'somenzz@163.com'])
    # `response` is keyed by message id and contains parsed,
    # converted response items.
    for message_id, data in client.fetch(messages, ['ENVELOPE']).items():
        envelope = data[b'ENVELOPE']
        print('{id}: subject: {subject} date: {date}'.format(
            id=message_id,
            subject = envelope.subject.decode('utf-8'),
            date = envelope.date
        ))
        break