from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from ...models import Profile, DocumentoFiscal
from . serializers import ProfileSerializer, DocumentoSerializer



class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
class DocumentoViewSet(viewsets.ModelViewSet):
    queryset =  DocumentoFiscal.objects.all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    
class TestJWTView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "JWT authentication sucessful"})
    