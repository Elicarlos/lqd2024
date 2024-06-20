from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . views import ProfileViewSet, DocumentoViewSet, TestJWTView


router = DefaultRouter()
router.register(r'profile', ProfileViewSet)
router.register(r'documentos', DocumentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test-jwt/', TestJWTView.as_view(), name='test_jwt')
]