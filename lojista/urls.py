from django.urls import path, re_path
from . import views
from django_filters.views import FilterView
from .filters import LojistaFilter
from django.conf.urls import handler404, handler500

app_name = 'lojista'

urlpatterns = [
    # Lojistas urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('list/', views.lojistalist, name='list'),
    re_path(r'^edit/(?P<id>[-\w]+)/$', views.editlojista, name='editlojista'),
    # path('search/', FilterView.as_view(filterset_class=LojistaFilter,
    #     template_name='lojista/lojistas_list.html'), name='search'),
    path('search/', views.search, name='search'),
    path('cupons/', views.cupons, name='cupons'),
    path('sorteio/', views.search_cupom, name='sorteio'),
    #re_path(r'^search/(?P<cpf>[-\w]+)$', views.search_cpf, name='searchbycpf'),
    # Ramo de atividades pathpatterns
    path('registeratividade/', views.registeratividade, name='registeratividade'),
    path('registerlocalizacao/', views.register_localizacao, name='register_localizacao'),
    path('listatividade/', views.listatividade, name='listatividade'),
    path('lista_localizacao/', views.lista_localizacao, name='lista_localizao'),
    path('lojistas-interessados/', views.lista_interessado, name='lista_interessado'),
    path('marcar_como_atendido/<int:adesao_id>/', views.marcar_como_atendido, name='marcar_como_atendido'),

    path('search/doc', views.reprint, name='search_by_doc'),
]

from django.conf.urls import handler404, handler500
