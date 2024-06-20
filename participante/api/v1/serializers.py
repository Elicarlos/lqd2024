from rest_framework import serializers
from ...models import DocumentoFiscal, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        
class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoFiscal
        fields = ['__all__']