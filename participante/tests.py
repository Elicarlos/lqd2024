
from .tests.test_views import RegisterViewTestCase
from participante.tasks import email_boas_vindas_task


def testar_envio_email():
    assunto = "Teste de E-mail"
    destinatario = "elicarlosantos_@hotmail.com"  # Substitua pelo seu e-mail de teste
    corpo = "Este é um e-mail de teste enviado para verificar a configuração."
    resultado = email_boas_vindas_task.apply_async(args=[assunto, destinatario, corpo])
    print(resultado.get())

