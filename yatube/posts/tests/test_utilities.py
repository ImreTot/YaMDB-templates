from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Saycoron')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for post in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост достаточной длины №{post}',
                group=cls.group
            )

    def setUp(self):
        cache.clear()
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        """Paginator формирует список из 10 постов на первой странице."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Paginator формирует список из 10 постов на второй странице."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
