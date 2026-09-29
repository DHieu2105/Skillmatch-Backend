import os
import smtplib
from email.message import EmailMessage


def send_password_reset_email(recipient: str, reset_link: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", username)

    if not all((host, username, password, sender)):
        return

    message = EmailMessage()
    message["Subject"] = "Reset your SkillMatch password"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Use this link to reset your SkillMatch password. "
        "It expires in 30 minutes:\n\n"
        f"{reset_link}"
    )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)