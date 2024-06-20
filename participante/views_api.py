from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from . models import Profile, DocumentoFiscal
from .serializers import ProfileSerializer, DocumentoSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = ['IsAuthenticated']
    
    
class DocumentoFiscalViewSet(viewsets.ModelViewSet):
    queryset = DocumentoFiscal.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = ['IsAuthenticated']
    