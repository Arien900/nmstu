# tests/test_models.py
from django.test import TestCase
from django.utils import timezone
from pc.models import User, Component, Build, BuildComponent, TimestampedModel


class TimestampedModelTest(TestCase):
    def test_created_at_updated_at(self):
        """Проверка автоматического заполнения created_at и updated_at"""
        user = User.objects.create_user(username="test", password="pass")
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertTrue(isinstance(user.created_at, timezone.datetime))
        self.assertTrue(isinstance(user.updated_at, timezone.datetime))


class ComponentModelTest(TestCase):
    def setUp(self):
        self.component = Component.objects.create(
            name="RTX 4070",
            category="GPU",
            price=65000,
            socket="",
            ram_type="",
            has_pcie=True
        )

    def test_component_creation(self):
        """Проверка создания компонента"""
        self.assertEqual(self.component.name, "RTX 4070")
        self.assertEqual(self.component.price, 65000)
        self.assertTrue(self.component.has_pcie)

    def test_string_representation(self):
        self.assertEqual(str(self.component), "RTX 4070 (GPU)")


class BuildModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.build = Build.objects.create(user=self.user, name="Test Build", total_price=100000)

    def test_build_creation(self):
        self.assertEqual(self.build.name, "Test Build")
        self.assertEqual(self.build.total_price, 100000)

    def test_unique_together_user_name(self):
        """Проверка ограничения уникальности (user, name)"""
        with self.assertRaises(Exception):
            Build.objects.create(user=self.user, name="Test Build", total_price=50000)


class BuildComponentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.build = Build.objects.create(user=self.user, name="Test", total_price=0)
        self.component = Component.objects.create(name="CPU", category="CPU", price=20000)
        self.build_component = BuildComponent.objects.create(
            build=self.build,
            component=self.component,
            quantity=1
        )

    def test_build_component_creation(self):
        self.assertEqual(self.build_component.build, self.build)
        self.assertEqual(self.build_component.component, self.component)
        self.assertEqual(self.build_component.quantity, 1)

    def test_build_components_relation(self):
        """Проверка обратной связи build.components (через related_name)"""
        self.assertEqual(self.build.components.count(), 1)
        self.assertEqual(self.build.components.first().component, self.component)