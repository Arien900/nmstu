from django.test import TestCase, Client
from django.urls import reverse
from pc.models import User, Component, Build
from django.contrib.auth.hashers import check_password


class SecurityTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_password_hashing(self):
        """Пароль хранится в хэше"""
        user = User.objects.create_user(username="test", password="mypassword")
        self.assertNotEqual(user.password, "mypassword")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(check_password("mypassword", user.password))

    def test_sql_injection_protection(self):
        """ORM защищает от SQL-инъекций"""
        # Даже с "опасным" именем — ORM экранирует
        dangerous_name = "'; DROP TABLE pc_user; --"
        Component.objects.create(
            name=dangerous_name,
            category="CPU",
            price=1000
        )
        comp = Component.objects.get(name=dangerous_name)
        self.assertEqual(comp.name, dangerous_name)  # данные сохранены как есть → нет инъекции

def test_xss_protection(self):
    """Шаблоны защищают от XSS"""
    # Создаём пользователя и сборку в тесте
    admin_user = User.objects.create_user(
        username="admin", password="pass", role="admin"
    )
    build = Build.objects.create(
        user=admin_user,
        name='<script>alert("xss")</script>',
        total_price=0
    )
    
    self.client.login(username="admin", password="pass")
    response = self.client.get(reverse('build', args=[build.id]))
    
    # В HTML должно быть экранировано:
    self.assertContains(response, '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;')
    self.assertNotContains(response, '<script>alert("xss")</script>')