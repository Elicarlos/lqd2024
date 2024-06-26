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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from django.utils.dateformat import DateFormat
from reportlab.graphics.barcode import qr
from base64 import b64encode
import logging
import bcp.settings as bcp_settings


@shared_task
def somar(x, y):
    return x + y
    

@shared_task
def generate_pdf_task(doc_id):
    
    font_size = bcp_settings.FONT_SIZE
    bar_height = bcp_settings.BAR_HEIGHT
    bar_width = bcp_settings.BAR_WIDTH
    font_name = bcp_settings.FONT_NAME
    font_path = bcp_settings.FONT_PATH
    font_bold = bcp_settings.FONT_PATH_BOLD
    font_name_bold = bcp_settings.FONT_BOLD
    image_path = bcp_settings.IMAGE_PATH
    image_rede = bcp_settings.IMAGE_PAGBANK
    image_master = bcp_settings.IMAGE_ELO
    image_cdl = bcp_settings.IMAGE_CDL

    doc = DocumentoFiscal.objects.select_related('user__profile').get(id=doc_id)
    cupons = Cupom.objects.filter(documentoFiscal=doc).select_related('documentoFiscal', 'documentoFiscal__user')
    profile = doc.user.profile

    pdfmetrics.registerFont(TTFont(font_name, font_path))
    pdfmetrics.registerFont(TTFont(font_name_bold, font_bold))

    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    def draw_fixed_elements():
        c.drawImage(image_path, 200, 683, mask='auto')
        c.drawImage(image_rede, 35, 750, mask='auto')
        c.drawImage(image_master, 400, 730, mask='auto')
        c.drawImage(image_cdl, 70, 90, mask='auto')
        c.setFont(font_name, 20)
        c.drawString(20, 660, '_______________________________________________________')
        c.setFont(font_name_bold, 23)
        c.drawString(150, 630, "Dados do Participante")

    for cupom in cupons:
        draw_fixed_elements()
        cupom.dataImpressao = datetime.now()
        code = cupom.get_info()
        qr_code = qr.QrCodeWidget(code)
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(100, 100, transform=[240. / width, 0, 0, 240. / height, 0, 0])
        d.add(qr_code)
        c.setFont("Helvetica", 30)
        c.setFont("Helvetica", 20)
        c.drawString(40, 550, "Nome:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(115, 550, f'{profile.nome}')
        c.setFont("Helvetica", 20)
        c.drawString(40, 580, "CPF:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(95, 580, f'{profile.CPF}')
        c.setFont("Helvetica", 20)
        c.drawString(40, 520, "Cidade:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(115, 520, f'{profile.cidade}')
        c.setFont("Helvetica", 20)
        c.drawString(330, 520, "Estado:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(410, 520, f'{profile.estado}')
        c.setFont("Helvetica", 20)
        c.drawString(40, 490, "Bairro:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(115, 490, f'{profile.bairro}')
        c.setFont("Helvetica", 20)
        c.drawString(330, 490, "Fone:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(390, 490, f'{profile.foneCelular1}')
        c.setFont("Helvetica", 20)
        c.drawString(40, 460, "Comprou na loja?")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, 430, f'{cupom.documentoFiscal.lojista}')
        c.setFont("Helvetica", 20)
        c.drawString(330, 460, "Vendedor:")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(330, 430, f'{cupom.documentoFiscal.vendedor}')
        c.setFont("Helvetica", 20)
        c.drawString(100, 390, "Qual a maior campanha de premios do Piauí?")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, 360, "(X) Liquida Teresina 2024")
        c.setFont("Helvetica", 20)
        c.drawString(40, 320, "Data:")
        c.setFont("Helvetica-Bold", 20)
        df = DateFormat(cupom.documentoFiscal.dataDocumento)
        c.drawString(100, 320, f'{df.format("d/m/Y")}')
        c.setFont("Helvetica", 40)
        c.drawString(80, 250, "CUPOM")
        c.setFont("Helvetica-Bold", 45)
        c.drawString(100, 200, f'{cupom.id}')
        c.drawString(20, 7, "_____________________________________________________")
        c.setFont("Helvetica-Bold", 20)
        c.drawString(150, 15, "SPA/ME N. ° 06.034371/2024")
        renderPDF.draw(d, c, 320, 80)
        c.showPage()

    c.save()

    pdf = buffer.getvalue()
    buffer.close()

    return b64encode(pdf).decode('utf-8')