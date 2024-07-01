from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def email_boas_vindas_task(assunto, destinatario, corpo, from_email='suporte@mg.liquidateresina.com.br', reply_to='suporte@mg.liquidateresina.com.br'):
 
    
    mail = EmailMessage(
        subject=assunto,
        from_email=from_email,
        to=[destinatario],
        body=corpo,
        headers={'Reply-To': reply_to}
    )
    mail.send()
    
    
@shared_task
def email_recuperacao_senha(assunto, destinatario, corpo, from_email="suporte@mg.liquidateresina.com.br", reply_to='suporte@mg.liquidateresina.com.br'):
    mail = EmailMessage(
        subject=assunto,
        from_email=from_email,
        to=[destinatario],
        body=corpo,
        headers={'Reply-To': reply_to}
    )
        
    
@shared_task
def email_notificacao_task(assunto, destinatario, corpo, from_email='suporte@mg.liquidateresina.com.br', reply_to='suporte@mg.liquidateresina.com.br'):
    mail = EmailMessage(
        subject=assunto,
        from_email=from_email,
        to=[destinatario],
        body=corpo,
        headers={'Reply-To': reply_to}
    )
    mail.send()
