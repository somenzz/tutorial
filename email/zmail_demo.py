import zmail
import settings
server = zmail.server(settings.account, settings.password)

# # Send mail
# server.send_mail('yourfriend@example.com',{'subject':'Hello!','content_text':'By zmail.'})
# # Or to a list of friends.
# server.send_mail(['friend1@example.com','friend2@example.com'],{'subject':'Hello!','content_text':'By zmail.'})

# Retrieve mail
latest_mail = server.get_latest()
zmail.show(latest_mail)