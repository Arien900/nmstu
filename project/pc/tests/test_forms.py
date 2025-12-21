# tests/test_forms.py
from django.test import TestCase
from pc.forms import CustomUserCreationForm


class UserCreationFormTest(TestCase):
    def test_valid_form(self):
        """Корректные данные → форма валидна"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_password_mismatch(self):
        """Пароли не совпадают → ошибка"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'pass1',
            'password2': 'pass2'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_required_field(self):
        """Нет username → ошибка"""
        form_data = {
            'email': 'test@example.com',
            'password1': 'pass',
            'password2': 'pass'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)