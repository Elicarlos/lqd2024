from celery import shared_task
from django.core.mail import send_mail
from cupom.models import Cupom
from participante.models import DocumentoFiscal, Profile
from django.db import transaction
from django.contrib.auth.models import User
from datetime import datetime

from django.shortcuts import get_object_or_404

from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfbase import pdfdoc
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from django.utils.dateformat import DateFormat
from reportlab.graphics.barcode import qr




@shared_task
def gerar_cupons_async(doc_id, operador_id):
    
    try:
        doc = DocumentoFiscal.objects.get(id=doc_id)
        qtde = int(doc.get_cupons())
        operador = User.objects.get(id=operador_id)
        print('Estou execultado minha task')

        # Cria uma lista de objetos Cupom a serem criados
        cupons = [
            Cupom(
                documentoFiscal=doc,
                user=doc.user,
                operador=operador,
                posto_trabalho=operador.profile.posto_trabalho
            )
            for _ in range(qtde)
        ]

        # Utiliza bulk_create para criar todos os cupons de uma vez
        with transaction.atomic():
            Cupom.objects.bulk_create(cupons)

    except DocumentoFiscal.DoesNotExist:
        pass
    except User.DoesNotExist:
        pass


