from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Saycoron')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост достаточной длины',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_urls_exist_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю."""
        templates_url = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/Saycoron/': 200,
            f'/posts/{self.post.id}/': 200,
            '/unexpecting_page/': 404,
        }
        for url, status_code in templates_url.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code, status_code,
                    f'Ответ общедоступной страницы -{url}- '
                    f'не возвращает требуемый status code -{status_code}-.')

    def test_create_post_by_author(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200,
                         'Ответ страницы create_post '
                         'не совпадает с ожидаемым.')

    def test_edit_post_by_author(self):
        """Страница редактирования поста доступна ее автору"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, 200,
                         'Ответ страницы edit_post не совпадает с ожидаемым.')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Saycoron/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template,
                                        f'URL-адрес -{url}- не использует '
                                        f'требуемый шаблон -{template}-.')

    def test_create_and_edit_post_url_redirect_anonymous_on_login(self):
        """Страницы создания и редактирования поста
        перенаправят неавторизованного пользователя
        на страницу авторизации."""
        templates_url = {
            '/create/':
                '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
        }
        for url, url_redirect in templates_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, url_redirect,
                    msg_prefix=f'Страница -{url}- не перенаправляет '
                               f'на страницу авторизации -{url_redirect}-.'
                )

    def test_edit_post_url_redirect_another_auth_user_to_profile(self):
        """Страница редактирования поста перенаправит не автора статьи
        на страницу post_detail поста."""
        self.another_user = User.objects.create_user(username='Sayk')
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)
        response = self.another_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')
