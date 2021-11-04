import smtplib
import ssl
import settings as settings
import src.services.log_service as log

# TODO: move to env
smtp_server = "smtp.gmail.com"
port = 587

# Create a secure SSL context
context = ssl.create_default_context()


# Try to log in to server and send email
def send_email(receiver_email, subject, message) -> str:
    email = """\
Subject: {0}

{1}""".format(subject, message)

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(settings.SMTP_EMAIL_ADDRESS, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL_ADDRESS, receiver_email, email)
    except Exception as err: # TODO: Catch specific exceptions and handle them
        log.log_error(err, "error while sending email")
        return "An error occurred"
    return "Invitation sent"
