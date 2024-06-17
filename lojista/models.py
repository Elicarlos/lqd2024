from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django_currentuser.db.models import CurrentUserField
from django.urls import reverse

class RamoAtividade(models.Model):
    """
    Model representando o ramo de atividade.
    """
    atividade = models.CharField(max_length=80, help_text='Informe o Ramo de Atividade. (exemplo: alimentação, vestuário, restaurante, etc.)')
    dataCadastro    = models.DateTimeField(verbose_name=u'Cadastrado em', auto_now_add=True, editable=False)   #nao vai aparecer na tela
    CadastradoPor   = CurrentUserField(verbose_name=u'Cadastrado Por', editable=False)
#    DataAlteracao   = models.DateTimeField(verbose_name=u'Alterado em', auto_now_add=True) #nao vai aparecer na tela
#    AlteradoPor_Id   = models.ForeignKey(User, blank=False, related_name='Cadastrado_por', editable=False, default=current_user.get_current_user)
    ativo = models.BooleanField(default=True)

    exclude =('ativo')

    class Meta:
        ordering = ['atividade']
        verbose_name = (u'ramo de Atividade')
        verbose_name_plural = (u'ramos de Atividades')

    def __str__(self):
        """
        String representando o Model object (in Admin site etc.)
        """
        return self.atividade
    
class Localizacao(models.Model):
    nome = models.CharField(max_length=250)
    descricao = models.TextField(blank=True)
    CadastradoPor   = CurrentUserField(verbose_name=u'Cadastrado Por', editable=False)
    
    def __str__(self):
        return self.nome
    


class Lojista(models.Model):
    CNPJLojista     = models.CharField(verbose_name=u'CNPJ do Lojista*', max_length=18, blank=False, null=True, unique=True, help_text=u'ex. 00.000.000/0000-00')
    IELojista       = models.CharField(verbose_name=u'Inscrição Estadual', max_length=14, blank=True, unique=False, null=True)
    razaoLojista    = models.CharField(verbose_name=u'Razão Social*', max_length=200, blank=True, null=True, help_text=u'Razão Social')
    fantasiaLojista = models.CharField(verbose_name=u'Nome Fantasia*', max_length=200, blank=False, help_text=u'Nome Fantasia')
    ramoAtividade   = models.ForeignKey('RamoAtividade', verbose_name=u'Ramo de Atividade*', on_delete=models.SET_NULL, null=True)
    localizacao  = models.ForeignKey(Localizacao, on_delete=models.SET_NULL, null=True,blank=True)
    dataCadastro    = models.DateTimeField(verbose_name=u'Cadastrado em', auto_now_add=True, editable=False)   #nao vai aparecer na tela
    CadastradoPor   = CurrentUserField(verbose_name=u'Cadastrado Por', editable=False)
    endereco        = models.CharField(verbose_name=u'Endereço', max_length=150, blank=True)
    telefone        = models.CharField(verbose_name=u'Telefone', max_length=150, blank=True, help_text=u'ex. (85)3212-0000')
#    CadastradoPor_Id = models.ForeignKey(User, editable=False, default=User.pk, on_delete=models.SET_NULL, null=True)
#    CadastradoPor_Id = models.ForeignKey(User, blank=False, related_name='Cadastrado_por', editable=False, default=current_user.get_current_user)
#    DataAlteracao   = models.DateTimeField(verbose_name=u'Alterado em', auto_now_add=True) #nao vai aparecer na tela
#    AlteradoPor_Id   = models.ForeignKey(User, blank=False, related_name='Cadastrado_por', editable=False, default=current_user.get_current_user)
    ativo           = models.BooleanField(default=True)

    exclude =('ativo')

    class Meta:
        ordering = ['fantasiaLojista']
        verbose_name = (u'lojista')
        verbose_name_plural = (u'lojistas')


    def __str__(self):
        """
        String representando o Objeto Participante.
        """
        return self.fantasiaLojista

    def get_absolute_url(self):
        return reverse('lojista:editlojista', args=[self.id])
    
class AdesaoLojista(models.Model):
    cnpj = models.CharField(verbose_name=u'Cnpj do Lojista', max_length=18, blank=False, null=True, unique=True, help_text=u'ex. 00.000.000/0000-00')
    razao_social = models.CharField(verbose_name='Razão Social', max_length=250, blank=False, null=True)
    fantasia = models.CharField(verbose_name='Nome Fantasia', max_length=250, blank=False, null=True)
    email = models.EmailField(verbose_name='Email', max_length=250, null=True, blank=False)
    telefone = models.CharField(verbose_name='Telefone', max_length=20, blank=False, null=True, help_text='(xx) xxxxx - xxxx')
    data_contato = models.DateTimeField(verbose_name='Data do contato', null=True, blank=True, help_text='Data e hora em que o vendedor entrou em contato ')
    atendido_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, help_text="Atendido por")
    atendido = models.BooleanField(default=False)
    
    def __str__(self):
        return self.fantasia or self.razao_social
    
    class Meta:
        verbose_name = 'Adesão de Lojista'
        verbose_name_plural = 'Adesões de Lojistas'
    
