from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from participante.models import Profile
from django.contrib.messages import get_messages

class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('participante:register')
        self.user_data = {
            'username': '249.118.300-50',  # CPF válido com 11 caracteres
            'password': 'teste123',  # Ajustado para password1 e password2
            'password2': 'teste123',
            'email': 'testuser@example.com',
            'nome': 'Test User',
            'CPF': '249.118.300-50',  # Supondo que CPF é username e válido
            'sexo': 'M',
            'foneCelular1': '1234567890',
            'endereco': 'Test Address',
            'bairro': 'Test Bairro',
            'cidade': 'Test Cidade',
            'estado': 'PI'
        }

    def test_register_page_accessible(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'participante/registerpart.html')

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data)
        user_exists = User.objects.filter(username=self.user_data['username']).exists()
        self.assertTrue(user_exists, "Usuário não foi criado corretamente")

    def test_register_user_duplicate(self):
        # Primeiro, criar um usuário com os dados fornecidos
        self.client.post(self.register_url, self.user_data)
        
        # Tentar registrar o mesmo usuário novamente
        response = self.client.post(self.register_url, self.user_data)
        messages = list(response.context['messages'])
        
        # Verifica se a mensagem de erro foi gerada
        self.assertTrue(any('Não foi possivel prosseguir! Já existe um participante com este CPF ou Email cadastrado!' in str(message) for message in messages))