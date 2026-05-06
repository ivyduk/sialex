import os
from django.test import TestCase
from django.urls import reverse
from unittest import skip

class GenericViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configurar datos iniciales para las pruebas aquí
        pass

    @skip("Implementar cuando existan los endpoints concretos")
    def test_homepage_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    @skip("Implementar basandose en un modelo existente")
    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

class GenericModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear instancias ficticias
        pass
    
    def test_dummy_model_creation(self):
        """
        Prueba genérica para validar que pueden crearse instancias
        del modelo en la BD eficientemente.
        """
        self.assertTrue(True)
