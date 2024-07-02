# tasks.py
from celery import shared_task
from django.core.mail import EmailMessage

@shared_task(rate_limit='6/m')
def email_boas_vindas_task(assunto, destinatario, corpo, from_email='suporte@mg.liquidateresina.com.br', reply_to='suporte@mg.liquidateresina.com.br'):
    mail = EmailMessage(
        subject=assunto,
        from_email=from_email,
        to=[destinatario],
        body=corpo,
        headers={'Reply-To': reply_to}
    )
    mail.send()

@shared_task(rate_limit='6/m')
def email_recuperacao_senha(assunto, corpo, from_email, destinatario, reply_to='suporte@mg.liquidateresina.com.br'):
    mail = EmailMessage(
        subject=assunto,
        body=corpo,
        from_email=from_email,
        to=destinatario,
        headers={'Reply-To': reply_to}
    )
    mail.send()

@shared_task(rate_limit='6/m')
def email_notificacao_task(assunto, destinatario, corpo, from_email='suporte@mg.liquidateresina.com.br', reply_to='suporte@mg.liquidateresina.com.br'):
    mail = EmailMessage(
        subject=assunto,
        from_email=from_email,
        to=[destinatario],
        body=corpo,
        headers={'Reply-To': reply_to}
    )
    mail.send()
