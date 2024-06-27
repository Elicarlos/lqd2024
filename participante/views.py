from calendar import month
from datetime import datetime
from decimal import Decimal
from pydoc import Doc
from unicodedata import decimal
from unittest import result
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from yaml import DocumentEndEvent
from .forms import *
from .models import Profile, DocumentoFiscal, PostoTrabalho
from lojista.models import Lojista, AdesaoLojista
from .filters import UserFilter, DocFilter
from django.db.models.functions import Lower, Upper
from cupom.forms import AddCupomForm
from cupom.models import Cupom
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction
from .forms import LoginForm, CepForm
from lojista.forms import FormLojistaAdesao
import requests
from django.contrib.auth.models import Group
from django.http import JsonResponse

from django.db import IntegrityError
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET



def not_found_page_view(request, exception):
    data = {}
    return render(request, 'not_found.html', data)

def server_error_view(request, exception):
    data = {}
    return render(request, 'not_found.html', data)

def main_page(request):
    login_form = LoginForm()
    return render(request, 'participante/coming_soon.html', {'section': 'homepage', 'lf': login_form})

@login_required
def doc_fiscal_done(request, doc_id):
    documentoFiscal = get_object_or_404(DocumentoFiscal, id=doc_id)
    return render(request, 'participante/doc_fiscal_done.html', {'new_documentoFiscal': documentoFiscal})

#backoffice
@login_required
@user_passes_test(lambda u: u.is_staff)
def backoffice(request):
    docs_list = DocumentoFiscal.objects.filter(pendente=True, enviado_por_operador=False).order_by('-dataCadastro')
    paginator = Paginator(docs_list, 100)
    page = request.GET.get('page', 1)
    docs = paginator.get_page(page)
    return render(request, 'participante/participante_backoffice.html', {'section': 'backoffice', 'docs': docs})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def search(request):
      user_list = Profile.objects.all().order_by(Upper('nome').asc())
      user_filter = UserFilter(request.GET, queryset=user_list)
      return render(request, 'participante/participante_list.html', {'filter': user_filter,
                                                                     'section': 'participantes'})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def search_by_cpf(request):
    if(request.GET.get('q')):
        if 'q' in request.GET is not None:
            cpf = request.GET.get('q')
            # profile = get_object_or_404(Profile, CPF=cpf)
            # user = get_object_or_404(User, username= profile.user.username)
            try:
                # user = User.objects.get(username=cpf)
                profile = Profile.objects.get(CPF=cpf)
                if profile:
                    docs = DocumentoFiscal.objects.filter(user=profile.user)
                    return render(request, 'participante/detail.html', {'section': 'people','user': profile, 'docs': docs})
            except Profile.DoesNotExist:
                messages.error(request, 'Participante não cadastrado no sistema')
                return render(request, 'participante/search_by_cpf.html')
        else:
            messages.error(request, 'CPF não encontrado!')
    return render(request, 'participante/search_by_cpf.html')

def participante_list(request):
    f = ParticipanteFilter(request.GET, queryset=Profile.objects.all())
    return render(request, 'participante/template.html', {'filter': f})


@login_required
@transaction.atomic
def register2(request):
    if request.method == 'POST':
        try:
            usuario_aux = User.objects.get(username=request.POST['username'])
            if usuario_aux:
                messages.error(request, 'Não foi possivel prosseguir! Já existe um participante com este CPF ou Email cadastrado!')
                user_form = UserRegistrationForm()
                profile_form = ProfileRegistrationForm()
            return render(request, 'participante/register.html', {'user_form': user_form, 'profile_form': profile_form})

        except User.DoesNotExist:
            user_form = UserRegistrationForm(request.POST)
            profile_form = ProfileRegistrationForm(request.POST,
                                                  files=request.FILES)
            if user_form.is_valid() and profile_form.is_valid():
                # Create a new user object but avoid saving it yet
                new_user = user_form.save(commit=False)
                # Set the chosen password
                new_user.set_password(user_form.cleaned_data['password'])
                # Save the User object
                new_user.save()
                # Create the user profile
                new_profile = profile_form.save(commit=False)
                new_profile.user = new_user
                new_profile.save()
                messages.success(request, 'Participante cadastrado com sucesso!')
                return render(request,
                              'participante/register_done2.html',
                              {'new_user': new_profile})
    else:
         user_form = UserRegistrationForm()
         profile_form = ProfileRegistrationForm()
    return render(request, 'participante/register.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def definir_posto(request):
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'reset_popup':
            request.session['show_popup'] = ''
            return JsonResponse({'success': True})
        else:
            posto_id = request.POST.get('posto_trabalho')
            posto = get_object_or_404(PostoTrabalho, id=posto_id)
            
            try:
                profile = request.user.profile
                profile.posto_trabalho = posto
                profile.save(update_fields=['posto_trabalho'])
                request.session['show_popup'] = ''  # Remover a variável da sessão após salvar
                return JsonResponse({'success': 'Posto de trabalho salvo com sucesso!'})
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Perfil não encontrado'}, status=404)
        
    return JsonResponse({'error': 'Método não permitido'}, status=405)



def homepage(request):    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'form_login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                cd = login_form.cleaned_data
                user = authenticate(username=cd['username'], password=cd['password'])
                if user is not None and user.is_active:
                    login(request, user)
                    if user.is_superuser:
                        request.session['show_popup'] = 'select_workstation'
                        
                    redirect_url = redirect('lojista:homepage' if user.is_superuser else 'participante:dashboard').url
                    return JsonResponse({'redirect_url': redirect_url})
                else:
                    return JsonResponse({'login_error': True, 'errors': {'__all__': ['Credenciais inválidas']}})
            else:
                errors = login_form.errors.get_json_data()
                return JsonResponse({'login_error': True, 'errors': errors})
        
        elif form_type == 'form_adesao':
            form_adesao = FormLojistaAdesao(request.POST)
            cnpj = request.POST.get('cnpj')
            
            if AdesaoLojista.objects.filter(cnpj=cnpj).exists():
                return JsonResponse({'error': True, 'message': 'CNPJ já cadastrado'})
            
            elif form_adesao.is_valid():
                form_adesao.save()
                return JsonResponse({'success': True, 'message': 'Cadastro realizado com sucesso!'})
            
            else:
                errors = form_adesao.errors.as_json()
                return JsonResponse({'error': True, 'message': 'Erro nos dados do formulário de adesão', 'errors': errors})

    else:
        login_form = LoginForm()
        form_adesao = FormLojistaAdesao()

    context = {
        'lf': login_form,
        'form_adesao': form_adesao,
    }

    return render(request, 'participante/index.html', context)

    # return render(request, 'participante/coming_soon.html', context)    
    # return render(request, 'participante/index.html', context)    
    # return render(request, 'participante/lojista_interessado.html', context)
        
                

   
   

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Autenticado com sucesso!')
                else:
                    return HttpResponse('Conta desativada!')
            else:
                return HttpResponse('Login inválido!')
    else:
        form = LoginForm()
    return render(request, 'participante/login.html', {'form': form})

@transaction.atomic
def register(request):
    if request.method == 'POST':
        try:
            usuario_aux = User.objects.get(username=request.POST['username'])
            usuario_email = User.objects.get(email=request.POST['email'])
            if usuario_aux or usuario_email:
                messages.error(request, 'Erro! Já existe um usuário com o mesmo e-mail')
                user_form = UserRegistrationForm()
                profile_form = ProfileRegistrationForm()
            return render(request, 'participante/registerpart.html', {'user_form': user_form, 'profile_form': profile_form})

        except User.DoesNotExist:
            user_form = UserRegistrationForm(request.POST)
            profile_form = ProfileRegistrationForm(request.POST, files=request.FILES)

            if user_form.is_valid() and profile_form.is_valid():
                # Create a new user object but avoid saving it yet
                new_user = user_form.save(commit=False)               

                # Set the chosen password
                new_user.set_password(user_form.cleaned_data['password'])
                # Save the User object
                new_user.save()
                # Create the user profile
                new_profile = profile_form.save(commit=False)
                
                new_profile.CPF = user_form.cleaned_data['username']

                new_profile.user = new_user
                new_profile.save()
                # subject = "Cadastro concluido com sucesso! Liquida Teresina 2024"
                # body = "Seu cadastro na promoção Liquida Teresina 2024 foi realizado com sucesso!"
                # email = EmailMessage(subject, body, to=[new_user.email])
                # email.send()
                return render(request,
                              'participante/register_done.html',
                              {'new_user': new_profile})

       
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileRegistrationForm()
    return render(request, 'participante/registerpart.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
@transaction.atomic
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil atualizado com sucesso')
            return render(request, 'participante/dashboard.html')
        else:
            messages.error(request, 'Erro na atualização do perfil')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'participante/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_detail(request, id):
    user = get_object_or_404(User, id=id, is_active=True)
    profile = get_object_or_404(Profile, user=user)
    docs_list = DocumentoFiscal.objects.filter(user=user)
    return render(request, 'participante/detail.html', {'section': 'people','user': profile, 'docs': docs_list})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def print_detail(request):
    docs_list = DocumentoFiscal.objects.filter(pendente=False, status=True).order_by('-dataCadastro')
    docs_list = Paginator(docs_list, 100)
    page = docs_list.page(request.GET.get('page', '1'))
    return render(request, 'participante/print_detail.html', {'section': 'people', 'docs': page})


@login_required
@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def user_edit(request, id):
    if request.method == 'POST':
        instance_user = get_object_or_404(User, id=id)
        instance_profile = get_object_or_404(Profile, user=instance_user)
        profile_form = ProfileEditForm(instance=instance_profile,
                                        data=request.POST,
                                        files=request.FILES)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Participante validado com sucesso')
        else:
            messages.error(request, 'Erro na validação do Participante')
    else:
        instance_user = get_object_or_404(User, id=id)
        instance_profile = get_object_or_404(Profile, user=instance_user)
        profile_form = ProfileEditForm(instance=instance_profile)
    return render(request, 'participante/editbyoperador.html', {'profile_form': profile_form})


@login_required
@transaction.atomic
def adddocfiscal(request):
    print('adddocfiscal')
    if request.method == 'POST':
        documentoFiscal_form = UserAddFiscalDocForm(request.POST, files=request.FILES)
        
        if documentoFiscal_form.is_valid():
            cnpj = documentoFiscal_form.cleaned_data['lojista_cnpj']
            print(cnpj)
            
            try:
                lojista = Lojista.objects.get(CNPJLojista=cnpj)
                new_documentoFiscal = documentoFiscal_form.save(commit=False)
                new_documentoFiscal.user = request.user
                new_documentoFiscal.lojista = lojista
                new_documentoFiscal.valorDocumento = documentoFiscal_form.cleaned_data.get('valorDocumento')
                new_documentoFiscal.save()
                
                messages.success(request, 'Documento adicionado com sucesso!')
                return redirect('participante:dashboard')
            
            except Lojista.DoesNotExist:
                messages.error(request, "Lojista não cadastrado na base de lojistas do Liquida Teresina 2024. <a href='https://wa.me/5586999950081?text=Ola%20preciso%20de%20suporte' style='color: #FFF'><b>|Informar ao Suporte|</b></a>")
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados fornecidos.')
    else:
        documentoFiscal_form = UserAddFiscalDocForm()
    
    return render(request, 'participante/doc_fiscal_add.html', {'documentoFiscal_form': documentoFiscal_form})




@login_required
@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def adddocfiscalbyop(request, id):
    user = get_object_or_404(User, id=id)
    is_superuser = request.user.is_superuser

    if request.method == 'POST':
        try:
            user_aux = User.objects.get(id=id)
            if is_superuser:
                documentoFiscal_form = UserAddFiscalDocFormSuperuser(request.POST, files=request.FILES)
            else:
                documentoFiscal_form = UserAddFiscalDocForm(request.POST, files=request.FILES)

            cnpj = documentoFiscal_form['lojista_cnpj'].value()
            numerodoc = documentoFiscal_form['numeroDocumento'].value()
            lojista = Lojista.objects.get(CNPJLojista=cnpj)

            if user_aux and lojista:
                if documentoFiscal_form.is_valid():
                    try:
                        new_documentoFiscal = documentoFiscal_form.save(commit=False)
                        new_documentoFiscal.user = user_aux
                        new_documentoFiscal.lojista = lojista
                        new_documentoFiscal.posto_trabalho = request.user.profile.posto_trabalho
                        new_documentoFiscal.enviado_por_operador = True
                        new_documentoFiscal.save()
                        return redirect('participante:user_detail', id=user.id)
                    except IntegrityError:
                        messages.error(request, 'Este documento já foi registrado para este lojista pelo usuário.')
                else:
                    messages.error(request, 'Ops! Parece que algo não está certo. Verifique se todas as informações estão corretas!')
            else:
                messages.error(request, 'Algo deu errado com o usuário ou lojista.')
        except Lojista.DoesNotExist:
            messages.error(request, 'O lojista do documento ainda não se encontra na nossa base de dados!')
            documentoFiscal_form = UserAddFiscalDocForm()
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {e}')
            documentoFiscal_form = UserAddFiscalDocForm()
    else:
        if is_superuser:
            documentoFiscal_form = UserAddFiscalDocFormSuperuser()
        else:
            documentoFiscal_form = UserAddFiscalDocForm()

    return render(request, 'participante/doc_fiscal_add_op.html', {'documentoFiscal_form': documentoFiscal_form, 'participante': user})



@login_required
def doclist(request):
    docs_list = DocumentoFiscal.objects.filter(user=request.user)
    docs_filter = DocFilter(request.GET, queryset=docs_list)
    return render(request, 'participante/list_doc_fiscal.html', {'filter': docs_filter,
                                                                   'section':'docsfiscais'})

@login_required
@transaction.atomic
def editdocfiscal(request, id):
    if request.method == 'POST':
        instance = get_object_or_404(DocumentoFiscal, id=id)
        documentofiscal_form = DocumentoFiscalEditForm(instance=instance,
                                                                        data=request.POST,
                                                                        files=request.FILES)
        if documentofiscal_form.is_valid():
            new_doc = documentofiscal_form.save(commit=False)
            new_doc.observacao = "Nenhuma"
            new_doc.save()
            messages.success(request, 'Documento Fiscal atualizado com sucesso!')
            return redirect('participante:dashboard')
        else:
            messages.error(request, 'Erro na atualização do documento Fiscal! verifique se não há algum dado incoerênte no formulario')
    else:
        instance = get_object_or_404(DocumentoFiscal, id=id)
        documentofiscal_form = DocumentoFiscalEditForm(instance=instance)
    return render(request, 'participante/doc_fiscal_edit.html', {'documentofiscal_form': documentofiscal_form})

@login_required
@transaction.atomic
def editdocfiscalbyop(request, id):
    if request.method == 'POST':
        instance = get_object_or_404(DocumentoFiscal.objects.select_for_update(), id=id)
        documentofiscal_form = DocumentoFiscalEditFormOp(instance=instance, data=request.POST, files=request.FILES)
        if documentofiscal_form.is_valid():
            documentofiscal_form.save()
            messages.success(request, 'Documento Fiscal atualizado com sucesso!')
        else:
            messages.error(request, 'Erro na atualização do documento Fiscal! verifique se não há algum dado incoerente no formulário')
    else:
        instance = get_object_or_404(DocumentoFiscal.objects.select_for_update(), id=id)
        documentofiscal_form = DocumentoFiscalEditFormOp(instance=instance)
    return render(request, 'participante/doc_fiscal_edit.html', {'documentofiscal_form': documentofiscal_form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
@transaction.atomic
def validadocfiscal(request, id):
    # Locking the row for update to prevent concurrent modifications
    instance = get_object_or_404(DocumentoFiscal.objects.select_for_update(), id=id, status=False)  # Adiciona condição para evitar validar já validados
    
    if request.method == 'POST':
        documentofiscal_form = DocumentoFiscalValidaForm(instance=instance, data=request.POST, files=request.FILES)
        if documentofiscal_form.is_valid():
            with transaction.atomic():
                new_doc = documentofiscal_form.save(commit=False)
                new_doc.qtde = int(new_doc.get_cupons())
                new_doc.status = not new_doc.pendente
                new_doc.posto_trabalho = request.user.profile.posto_trabalho
                new_doc.save()

                if not new_doc.pendente:
                    if Cupom.objects.filter(documentoFiscal=new_doc).exists():
                        messages.error(request, 'Cupons já foram gerados para este documento fiscal.')
                        return redirect('participante:user_detail', id=new_doc.user.id)
                    
                    cupons = [
                        Cupom(
                            documentoFiscal=new_doc,
                            user=new_doc.user,
                            operador=request.user,
                            posto_trabalho=request.user.profile.posto_trabalho
                        ) for _ in range(new_doc.qtde)
                    ]
                    Cupom.objects.bulk_create(cupons)
                    messages.success(request, 'Documento Fiscal validado com sucesso, agora você pode Imprimir os cupons')
                else:
                    messages.info(request, f'O documento fiscal {new_doc.numeroDocumento} não foi validado por pendências. Se está tudo certo com o documento, por favor repita novamente o procedimento de validação e desmarque a opção de pendente para que o mesmo seja validado! Se você encontrou pendências no documento em questão, por favor não esqueça de descrevê-las no campo observações!')

                return redirect('participante:user_detail', id=new_doc.user.id)

        messages.error(request, 'Ocorreu um erro durante o processo de validação. Verifique se não há algum dado incoerente no formulário!')

    else:
        documentofiscal_form = DocumentoFiscalValidaForm(instance=instance)

    return render(request, 'participante/doc_fiscal_valida.html', {'documentofiscal_form': documentofiscal_form, 'doc': instance})


@login_required
def dashboard(request):
    if request.user.is_superuser: return render(request, 'lojista/dashboard.html', {'section': 'lojista'})
    docs = DocumentoFiscal.objects.filter(user=request.user)
    return render(request, 'participante/dashboard.html', {'section': 'dashboard','docs': docs})

@login_required
def lojista(request):
    return render(request, 'not_found.html', {'section': 'coupons'})

@login_required
def coupons(request):
    return render(request, 'participante/coupons.html', {'section': 'coupons'})

@login_required
def premios(request):
    return render(request, 'participante/premios.html', {'section': 'premios'})

from django.db.models.functions import TruncMonth, TruncDate

from django.db.models.aggregates import Count, Avg, Min, Max, Sum
from django.db.models import Count, F

# from django.db.models.functions import ExtractDay, ExtractMonth, ExtractQuarter, ExtractIsoWeekDay, ExtractWeekDay, ExtractIsoYear, ExtractYear


@login_required
@user_passes_test(lambda u: u.is_superuser)
def dados_campanha(request):
    quant_cupons = Cupom.objects.all().count()
    
    quant_usuario = Profile.objects.filter(user__is_superuser=False).count()
    quant_lojistas = Lojista.objects.count()    
    quant_documentos = DocumentoFiscal.objects.count()
    # lojista = DocumentoFiscal.objects.select_related('lojista', 'user')

    labels = []
    data = []
    data_faturamento = []
    valor_faturamento = []
    # da = get_data(cupons)
    # print("Resultado da Funcao >>>>>>>>>>", data)
    # cup = Cupom.objects.values('dataCriacao').annotate(total=Count(data))
    bu = Cupom.objects.all().annotate(date=TruncDate('dataCriacao')).values('date').annotate(Count('dataCriacao')).order_by('date')
    faturamento_por_dia = DocumentoFiscal.objects.all().annotate(date=TruncDate('dataCadastro')).values('date').annotate(valor=Sum('valorDocumento')).order_by('date')
    # q1 = DocumentoFiscal.objects.select_related('user').annotate(total=Sum('valorDocumento'))

    # for q in q1:
    #     print('Cliente', q.user.profile.nome, 'Total', q.total)

    q1 = DocumentoFiscal.objects.all().select_related('user')
    q2 = q1.values('user__profile__CPF', 'user__profile__nome').annotate(total=Sum('valorDocumento'), virtual=Sum('valorVirtual'))
    q3 = q2.order_by('-total', '-user__profile__CPF')[:10]
    cliente_cpf = []
    total_cpf = []

    for q in q3:
        cliente_cpf.append(q['user__profile__CPF'])
        total = float(q['total'])
        total_cpf.append(total)

    
    

    cupons_por_operador = (
    Cupom.objects
    .values('operador__first_name')
    .annotate(cupom_count=Count('id'))
    .order_by('-cupom_count')
    )

    # Query para obter informações sobre os operadores, incluindo o first_name
    operadores_info = [
        {'operador': item['operador__first_name'], 'cupom_count': item['cupom_count']}
        for item in cupons_por_operador
    ]

    
    



    grupos = Group.objects.filter(name__in=["Teresina Shopping", "Riverside","Rio Poty", "Pintos Dirceu"])

    labels_grupo = []
    data_cupons_por_grupo = []

    for grupo in grupos:
        operadores_do_grupo = User.objects.filter(groups=grupo)
        cupons_por_grupo = Cupom.objects.filter(operador__in=operadores_do_grupo).count()
        labels_grupo.append(grupo.name)
        data_cupons_por_grupo.append(cupons_por_grupo)


       
        
    for fat in faturamento_por_dia:
        dt = fat['date']
        dt = datetime.strftime(dt,"%d/%m")
        data_faturamento.append(dt)
        fat = float(fat['valor'])        
        valor_faturamento.append(fat)



    for b in bu:
        dt = b['date']
        dt = datetime.strftime(dt,"%d/%m")        
        labels.append(dt)
        data.append(b['dataCriacao__count'])


    quant_doc_ramoAtividade = DocumentoFiscal.objects.all().select_related('lojista')
    query_ramoAtividade = quant_doc_ramoAtividade.values('lojista__ramoAtividade__atividade').annotate(total=Count('id'))
    ramo_atividade = []
    quant_ramo_atividade = []

   
    for q in query_ramoAtividade:
        # atividade = q['lojista__ramo__atividade']
        atividade = q['lojista__ramoAtividade__atividade']
        ramo_atividade.append(atividade)
        total = q['total']
        quant_ramo_atividade.append(total)     

    

    operadores = User.objects.filter(is_staff=True).count()
    faturamento_total = DocumentoFiscal.objects.aggregate(total=Sum('valorDocumento'))
    faturamento_total = faturamento_total['total']
    if faturamento_total is None:
        faturamento_total = 0
        ticket_medio = 0
    
    else:
        ticket_medio = float(faturamento_total / quant_documentos) 

   

    context = {
        'labels': labels,
        'data': data,      
        'data_faturamento': data_faturamento,
        'valor_faturamento': valor_faturamento,
        'ramo_atividade': ramo_atividade,
        'quant_ramo_atividade':quant_ramo_atividade,
        'cliente_cpf': cliente_cpf,
        'total_cpf': total_cpf,
        'operadores_info': operadores_info,
        'labels_grupo': labels_grupo,
        'data_cupons_por_grupo': data_cupons_por_grupo,
        'quant_cupons': quant_cupons,
        'quant_usuario': quant_usuario,
        'quant_lojistas': quant_lojistas,
        'quant_documentos': quant_documentos,
        'operadores': operadores,
        'faturamento_total': faturamento_total,
        'ticket_medio': ticket_medio,       
    }
    return render(request, 'dash/index.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def graficos(request):    
    labels = []
    data = []
    data_faturamento = []
    valor_faturamento = []
    # da = get_data(cupons)
    # print("Resultado da Funcao >>>>>>>>>>", data)
    # cup = Cupom.objects.values('dataCriacao').annotate(total=Count(data))
    bu = Cupom.objects.all().annotate(date=TruncDate('dataCriacao')).values('date').annotate(Count('dataCriacao')).order_by('date')
    faturamento_por_dia = DocumentoFiscal.objects.all().annotate(date=TruncDate('dataCadastro')).values('date').annotate(valor=Sum('valorDocumento')).order_by('date')
    # q1 = DocumentoFiscal.objects.select_related('user').annotate(total=Sum('valorDocumento'))

    # for q in q1:
    #     print('Cliente', q.user.profile.nome, 'Total', q.total)

    q1 = DocumentoFiscal.objects.all().select_related('user')
    q2 = q1.values('user__profile__CPF', 'user__profile__nome').annotate(total=Sum('valorDocumento'), virtual=Sum('valorVirtual'))
    q3 = q2.order_by('-total', '-user__profile__CPF')[:10]
    cliente_cpf = []
    total_cpf = []

    for q in q3:
        cliente_cpf.append(q['user__profile__CPF'])
        total = float(q['total'])
        total_cpf.append(total)

    
    cupons_por_operador = Cupom.objects.values('operador__username').annotate(cupom_count=Count('id'))
    operadores_info = [
        {'operador': item['operador__username'], 'cupom_count': item['cupom_count']}
        for item in cupons_por_operador
    ]



    grupos = Group.objects.filter(name__in=["Teresina Shopping", "Riverside"])

    labels_grupo = []
    data_cupons_por_grupo = []

    for grupo in grupos:
        operadores_do_grupo = User.objects.filter(groups=grupo)
        cupons_por_grupo = Cupom.objects.filter(operador__in=operadores_do_grupo).count()
        labels_grupo.append(grupo.name)
        data_cupons_por_grupo.append(cupons_por_grupo)


    



    
    
        
    for fat in faturamento_por_dia:
        dt = fat['date']
        dt = datetime.strftime(dt,"%d/%m")
        data_faturamento.append(dt)
        fat = float(fat['valor'])        
        valor_faturamento.append(fat)



    for b in bu:
        dt = b['date']
        dt = datetime.strftime(dt,"%d/%m")        
        labels.append(dt)
        data.append(b['dataCriacao__count'])


    quant_doc_ramoAtividade = DocumentoFiscal.objects.all().select_related('lojista')
    query_ramoAtividade = quant_doc_ramoAtividade.values('lojista__ramoAtividade__atividade').annotate(total=Count('id'))
    ramo_atividade = []
    quant_ramo_atividade = []

   
    for q in query_ramoAtividade:
        # atividade = q['lojista__ramo__atividade']
        atividade = q['lojista__ramoAtividade__atividade']
        ramo_atividade.append(atividade)
        total = q['total']
        quant_ramo_atividade.append(total)     

    
    
    
    

    context = {        
        'labels': labels,
        'data': data,      
        'data_faturamento': data_faturamento,
        'valor_faturamento': valor_faturamento,
        'ramo_atividade': ramo_atividade,
        'quant_ramo_atividade':quant_ramo_atividade,
        'cliente_cpf': cliente_cpf,
        'total_cpf': total_cpf,
        'operadores_info': operadores_info,
        'labels_grupo': labels_grupo,
        'data_cupons_por_grupo': data_cupons_por_grupo,
    
    }
    return render(request, 'dash/charts.html', context)




def relatorios_camp(request):    
    return render(request, 'dash/tables.html'  )



'''from utils.ticket import validarticket
#FUNCOES PARA GERACAO DE TICKETS
def gerarticket(request):
    return render(request, 'ticket/pages/home.html', context={
        'ticket': validarticket
    })'''


def consulta_cep(request):
    form = CepForm(request.POST or None)

    

    return render(request, 'participante/form.html', {'form': form})


def resumo_lojistas(request):
    # documento = Momde
    return render(request, 'dash/tables.html')
