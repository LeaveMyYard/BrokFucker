import smtplib
from flask import request
from lib.settings import Settings

class EmailSender:

    @staticmethod
    def send(to: str, subject: str, body: str):
        host, port, user, password = Settings.get_smtp_data()
        sent_from = user

        email_text = (
            f"From: {sent_from}\n"
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"\n"
            f"{body}"
        )

        server = smtplib.SMTP_SSL(host, port)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sent_from, to, email_text)
        server.close()

    @staticmethod
    def send_email_verification(email: str, code: str):
        EmailSender.send(
            email,
            "Email confirmation",
            f"{request.host_url}api/v1/register/verify/{code}"
        )