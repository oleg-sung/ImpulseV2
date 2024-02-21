import smtplib

from configuration.config import settings


class EmailTools:
    def __init__(self):
        self.user = settings.MAIL_USERNAME
        self.passwd = settings.MAIL_PASSWORD
        server = settings.MAIL_SERVER
        port = settings.MAIL_PORT
        self.smtp = smtplib.SMTP(server, port)

    def send_email(self, recipient: str, subject: str, body: str):
        try:
            self.smtp.starttls()
            self.smtp.ehlo()
            self.smtp.login(self.user, self.passwd)
            mime = "MIME-Version:  1.0"
            charset = "Content-Type: text/plain; charset=utf-8"
            body = "\r\n".join(
                (
                    f"From: {self.user}",
                    f"To: {recipient}",
                    f"Subject: {subject}",
                    mime,
                    charset,
                    "",
                    body,
                )
            )
            self.smtp.sendmail(from_addr=self.user, to_addrs=recipient, msg=body)
        except smtplib.SMTPException as err:
            print("Что-то пошло не так...")
        finally:
            self.smtp.quit()
