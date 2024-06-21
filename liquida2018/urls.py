"""liquida2018 URL Configuration
"""
from django.urls import include, path, re_path

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from participante import urls as purls
from lojista import urls as lurls
from cupom import urls as curls
from bcp import urls as burls
from django.conf.urls import handler404, handler500
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# handler404 = 'participante.views.not_found_page_view'
# handler500 = 'participante.views.server_error_view'

urlpatterns = [
    path('', include(purls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('op-admin-nimda-solu/', admin.site.urls),
    re_path(r'^cupom/', include(curls, namespace='cupom')),
    path('lojista/', include(lurls, namespace='lojista')),
    path('barcode/', include(burls, namespace='bcp')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/participante/v1/', include('participante.api.v1.urls')),
    
    # python-social-auth
    #url('social-auth/', include('social.apps.django_app.urls', namespace='social')),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Administração Liquida Teresina"
admin.site.site_title = "Liquida Teresina"
admin.site.index_title = "Bem vindo a administração do Liquida Teresina"
