from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from blog.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User


@shared_task
def send_verification_email_task(user_id, email_address, domain, protocol):
    user = User.objects.get(id=user_id)
    message_subject = "Activate your account"
    message_content = render_to_string(
        "blog/email_message/message_verify_account.html",
        {
            "user": user.username,
            "domain": domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": protocol,
        },
    )
    # Specify parameters for sending a verification email
    email = EmailMessage(message_subject, message_content, to=[email_address])
    success = email.send()

    if success:
        print(f"Success! Activation link sent to {email_address}.")
    else:
        print(f"Error sending email to {email_address}.")
