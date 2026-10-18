import os
import smtplib
from email.message import EmailMessage

# Read env vars (optionally set these in a .env file or your environment)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465") or 465)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "no-reply@example.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def _send_via_smtp(to_email: str, subject: str, body: str, html: str = None):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    if html:
        msg.set_content(body)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(body)

    if not SMTP_HOST:
        # No SMTP configured — print to console (safe fallback for development)
        print("=== Email (console fallback) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(body)
        if html:
            print("[HTML]")
            print(html)
        print("=== End email ===")
        return

    # send via SMTP
    try:
        # Use SSL if port suggests it, otherwise use starttls
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        # On failure, print to console (do not crash background task)
        print(f"Failed to send email to {to_email}: {e}")
        print("Falling back to console output:")
        print("Subject:", subject)
        print("Body:", body)
        if html:
            print("HTML:", html)

def send_verification_email(to_email: str, username: str, token: str):
    verify_link = f"{FRONTEND_URL}/verify-email?token={token}"
    subject = "Verify your email"
    body = (
        f"Hi {username},\n\n"
        "Please verify your email address by clicking the link below:\n\n"
        f"{verify_link}\n\n"
        "If you did not sign up, please ignore this message.\n"
    )
    html = f"""
    <p>Hi {username},</p>
    <p>Please verify your email address by clicking the link below:</p>
    <p><a href="{verify_link}">Verify email</a></p>
    <p>If you did not sign up, please ignore this message.</p>
    """
    _send_via_smtp(to_email, subject, body, html)

def send_password_reset_email(to_email: str, username: str, token: str):
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    subject = "Password reset request"
    body = (
        f"Hi {username},\n\n"
        "We received a request to reset your password. Click the link below to set a new password:\n\n"
        f"{reset_link}\n\n"
        "If you did not request a password reset, you can ignore this message.\n"
    )
    html = f"""
    <p>Hi {username},</p>
    <p>We received a request to reset your password. Click the link below to set a new password:</p>
    <p><a href="{reset_link}">Reset password</a></p>
    <p>If you did not request a password reset, you can ignore this message.</p>
    """
    _send_via_smtp(to_email, subject, body, html)