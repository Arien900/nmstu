from django.test import TestCase, Client
from django.urls import reverse
from pc.models import User, Component, Build, BuildComponent  


class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="pass", role="user")
        self.admin = User.objects.create_user(username="admin", password="pass", role="admin")
        self.component = Component.objects.create(name="CPU", category="CPU", price=20000)

    def test_home_anonymous(self):
        """Гость → 200 на главной"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_required_pages(self):
        """Гость → редирект на /login/ при доступе к защищённым страницам"""
        urls = ['create_build', 'presets', 'build', 'admin_dashboard']
        for url_name in urls:
            if url_name == 'build':
                url = reverse(url_name, args=[1])
            elif url_name == 'admin_dashboard':
                url = reverse(url_name)
            else:
                url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))

    def test_admin_access(self):
        """Обычный пользователь в ошибку 403 на админке"""
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_admin_dashboard(self):
        """Админ → 200 на админке"""
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_build(self):
        """Создание сборки → редирект + сообщение + сохранение в БД"""
        self.client.login(username="user", password="pass")
        response = self.client.post(reverse('create_build'), {
            'name': 'My Build',
            'components': [self.component.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/build/'))
        self.assertEqual(Build.objects.count(), 1)
        build = Build.objects.first()
        self.assertEqual(build.name, "My Build")
        self.assertEqual(build.components.count(), 1)

    def test_build_detail(self):
        """Просмотр сборки → 200, компоненты отображаются"""
        build = Build.objects.create(user=self.user, name="Test", total_price=20000)
        BuildComponent.objects.create(build=build, component=self.component)
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse('build', args=[build.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CPU")
        self.assertContains(response, "20000")

    def test_delete_build(self):
        """Удаление сборки → 302, сборка удаляется из БД"""
        build = Build.objects.create(user=self.user, name="ToDelete", total_price=0)
        self.client.login(username="user", password="pass")
        response = self.client.post(reverse('delete_build', args=[build.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Build.objects.count(), 0)