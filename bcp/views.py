from bcp.tasks import generate_pdf_task
from cupom.models import Cupom
from django.db import transaction
from participante.models import DocumentoFiscal, Profile
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from participante.forms import DocumentoFiscalEditForm
from cryptography.fernet import Fernet

from reportlab.graphics.shapes import String, Drawing
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.pdfbase import pdfdoc
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from django.utils.dateformat import DateFormat
from datetime import datetime
from silk.profiling.profiler import silk_profile
from celery.result import AsyncResult
from django.http import JsonResponse

# from django.contrib.staticfiles.templatetags.staticfiles import static
from django.templatetags.static import static
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO

@login_required
@user_passes_test(lambda u: u.is_superuser)
def print_barcode_embed_example(request, id_, template='cupons_impressos.html'):
    """
    This is a test page showing how you can embed a request to print a barcode
    """
    doc = get_object_or_404(DocumentoFiscal, id=id_)
    if not doc.status and not request.user.is_staff:
        return render(request, 'lojista/dashboard.html')
    doc_form = DocumentoFiscalEditForm(instance=doc)
    new_doc = doc_form.save(commit=False)
    new_doc.key = Fernet.generate_key()
    new_doc.status = False
    new_doc.save()
    bcp_url = reverse('bcp:print_qrcode', kwargs = {'id_': id_,})
    context = { 'bcp_url': bcp_url, 'doc':doc, }
    return render(request, template, context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def print_qrcode(request, id_, template='print.html'):
    """
    This page causes the browser to request the barcode be printed
    """
    doc = get_object_or_404(DocumentoFiscal, id=id_)
    doc_form = DocumentoFiscalEditForm(instance=doc)
    new_doc = doc_form.save(commit=False)
    new_doc.status = False
    new_doc.save()
    pdf_url = reverse('bcp:generate', kwargs = {'id_': id_, })
    context = { 'pdf_url': pdf_url, }
    return render(request, template, context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def print_barcode(request, id_, template='print.html'):
    """
    This page causes the browser to request the barcode be printed
    """
    doc = get_object_or_404(DocumentoFiscal, id=id_)
    doc_form = DocumentoFiscalEditForm(instance=doc)
    new_doc = doc_form.save(commit=False)
    new_doc.status = False
    new_doc.save()
    # doc = get_object_or_404(DocumentoFiscal, id=id_)
    pdf_url = reverse('bcp:generate', kwargs = {'id_': id_,})
    context = { 'pdf_url': pdf_url, 'doc':doc }
    return render(request, template, context)
        

@login_required
@user_passes_test(lambda u: u.is_superuser)
@silk_profile(name='Generate PDF')
def generate(request, id_, barcode_type='Standard39', auto_print=True):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename={id_}.pdf'

    # Configurações
    import bcp.settings as bcp_settings
    font_size = bcp_settings.FONT_SIZE
    bar_height = bcp_settings.BAR_HEIGHT
    bar_width = bcp_settings.BAR_WIDTH
    font_name = bcp_settings.FONT_NAME
    font_path = bcp_settings.FONT_PATH
    font_bold = bcp_settings.FONT_PATH_BOLD
    font_name_bold = bcp_settings.FONT_BOLD
    image_path = bcp_settings.IMAGE_PATH
    image_rede = bcp_settings.IMAGE_REDE
    image_master = bcp_settings.IMAGE_MASTER
    image_cdl = bcp_settings.IMAGE_CDL

    doc = get_object_or_404(DocumentoFiscal, id=id_)
  
    doc = get_object_or_404(DocumentoFiscal.objects.select_related('user__profile'), id=id_)
    cupons = Cupom.objects.filter(documentoFiscal=doc).select_related('documentoFiscal').prefetch_related('documentoFiscal__user')
    profile = doc.user.profile


    # Registro da fonte
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    pdfmetrics.registerFont(TTFont(font_name_bold, font_bold))

    # Configurar JS para impressão automática
    if auto_print:
        pdfdoc.PDFCatalog.OpenAction = '<</S/JavaScript/JS(this.print({bUI:false,bSilent:true,bShrinkToFit:true}));>>'
        pdfdoc.PDFInfo.title = 'Liquida Teresina 2024'

    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    def draw_fixed_elements():
        c.drawImage(image_path, 210, 685, mask='auto')
        c.drawImage(image_rede, 35, 688, mask='auto')
        c.drawImage(image_master, 400, 688, mask='auto')
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

    response.write(pdf)
    return response

