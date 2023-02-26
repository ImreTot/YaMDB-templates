from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост достаточной длины',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_titles = {
            self.post: 'Тестовый пост д',
            self.group: 'Тестовая группа',
        }
        for value, expected in field_titles.items():
            with self.subTest(value=value):
                self.assertEqual(
                    str(value), expected,
                    f'Название экземпляра -{value}- модели '
                    f'формируется неверно. '
                    f'Ожидаемое значение -{expected}-.')
