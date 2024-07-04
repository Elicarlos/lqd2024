"""
Module: Barcode Printer URLS
Project: Django BCP
Copyright: Adlibre Pty Ltd 2012
License: See LICENSE for license information
"""


from . import views
from django.contrib.auth.views import *
from django.urls import path, re_path
from django.conf.urls import handler404, handler500
#import mdtui.views

app_name = 'bcp'

urlpatterns = [
    re_path(r'^(?P<id_>[-\w]+)$', views.generate, name='generate'),
    re_path(r'^(?P<id_>[-\w]+)/print$', views.print_barcode, name='print'),
    re_path(r'^(?P<id_>[-\w]+)/print_qrcode$', views.print_qrcode, name='print_qrcode'),
    re_path(r'^(?P<id_>[-\w]+)/test', views.print_barcode_embed_example, name='embed-example'),
    path('check_task_status/<str:task_id>/', views.check_task_status, name="check_task_status"),
    # path('success/<str:task_id>/', views.success_page, name='success')
    
    
    # path('regulamento/', views.regulamento, name='regulamento'),
]
# handler404 = 'participante.views.not_found_page_view'
# handler500 = 'participante.views.server_error_view'