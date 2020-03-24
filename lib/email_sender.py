import smtplib
from flask import request, render_template
from lib.settings import Settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    @staticmethod
    def send(to: str, subject: str, body: str):
        host, port, user, password = Settings.get_smtp_data()

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = to

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP_SSL(host, port)
        server.ehlo()
        server.login(user, password)
        server.sendmail(user, to, msg.as_string())
        server.close()

    @staticmethod
    def send_email_verification(email: str, code: str):
        EmailSender.send(
            email,
            "Email confirmation",
            render_template(
                'email_verification.html',
                action_url = f"{request.host_url}{Settings.get_email_verification_link_base()}?code={code}"
            )
        )

    @staticmethod
    def send_password_change_verification(email: str, code: str):
        EmailSender.send(
            email,
            "New password confirmation",
            render_template(
                'password_change_verification.html',
                action_url = f"{request.host_url}{Settings.get_new_password_verification_link_base()}?code={code}"
            )
        )

    @staticmethod
    def send_account_restore_verification(email: str, code: str):
        EmailSender.send(
            email,
            "Forgot a password confirmation",
            render_template(
                'account_restore_verification.html',
                action_url = f"{request.host_url}{Settings.get_account_restore_verification_link_base()}?code={code}"
            )
        )