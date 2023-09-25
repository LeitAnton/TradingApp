from django.core.mail import send_mail

from TradingApp.celery import app


@app.task
def send_mail_about_reset_password(password, email):
    send_mail(
        subject='Reset password',
        message=f'Your new password: {password}',
        from_email=None,
        recipient_list=[email],
        fail_silently=False
    )
