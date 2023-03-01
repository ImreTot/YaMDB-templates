from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Saycoron')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Еще одна тестовая группа',
            slug='another_test-slug',
            description='Другое тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост достаточной длины',
            group=cls.group
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Saycoron'}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                'posts/post_create.html',
        }

        for reverse_name, template in template_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница -{reverse_name}- '
                    f'не использует правильный шаблон -{template}-.')

    def test_create_post_show_correct_context(self):
        """Шаблон form в create_post сформирован правильно."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон form в edit_post сформирован правильно."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_correct_context(self):
        """Данные в context шаблона index переданы корректно."""
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_group_list_show_correct_context(self):
        """Данные в context шаблона group_list переданы корректно."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_profile_show_correct_context(self):
        """Данные в context шаблона profile переданы корректно."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'Saycoron'},
        ))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_post_detail_show_correct_context(self):
        """Данные в context шаблона post_detail переданы корректно."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        first_object = response.context['current_post']
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)

    def test_post_with_group_in_correct_place(self):
        """Пост с указанной группой находится в нужных словарях context."""
        template_pages = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Saycoron'}),
        ]
        for page in template_pages:
            with self.subTest(page=page):
                self.assertIn(self.post,
                              self.guest_client.get(page).context['page_obj'],
                              f'Ошибка в словаре context. Поста с группой '
                              f'нет на соответствующей странице -{page}-.')

    def test_post_with_group_not_in_wrong_place(self):
        """Пост с указанной группой
        не появляется в списке context другой группы"""
        response = self.guest_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'another_test-slug'}))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_auth_user_may_post_comment(self):
        """Комментировать посты может авторизованный пользователь."""
        first_comments_count = Comment.objects.count()
        form_data = {'text': 'тестовый комментарий.'}
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(first_comments_count + 1,
                         Comment.objects.count())

    def test_guest_user_cant_comment_posts(self):
        """Комментировать посты не авторизованный пользователь не может."""
        first_comments_count = Comment.objects.count()
        form_data = {'text': 'тестовый комментарий.'}
        self.guest_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(first_comments_count,
                         Comment.objects.count())

    def test_model_save_correct_comment(self):
        """View-функция add_comment корректно сохраняет новый комментарий."""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='тестовый комментарий.'
        )
        self.assertEqual(comment.text, 'тестовый комментарий.')

    def test_follow_index_return_correct_authors_list(self):
        """View-функция follow_index возвращает список постов,
        на которые подписан пользователь."""
        following_author = User.objects.create_user(username='Second')
        Follow.objects.create(user_id=self.user.id,
                              author_id=following_author.id)
        second_post = Post.objects.create(
            author=following_author,
            text='Очень интересный тестовый пост достаточной длины',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(second_post, response.context['page_obj'])

    def test_profile_follow_create_subscription(self):
        """View-функиция profile_follow
        создает подписку на выбранного автора."""
        following_author = User.objects.create_user(username='Second')
        second_post = Post.objects.create(
            author=following_author,
            text='Очень интересный тестовый пост достаточной длины',
        )
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': following_author}
        ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(second_post, response.context['page_obj'])

    def test_profile_unfollow_create_subscription(self):
        """View-функция profile_unfollow
        удаляет подписку на выбранного автора."""
        following_author = User.objects.create_user(username='Second')
        second_post = Post.objects.create(
            author=following_author,
            text='Очень интересный тестовый пост достаточной длины',
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': following_author}
        ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(second_post, response.context['page_obj'])

    def test_following_author_doesnt_appear_in_wrong_feed(self):
        """Подписка одного пользователя на конкретного автора
        не появляется у другого пользователя."""
        following_author = User.objects.create_user(username='Second')
        second_user = User.objects.create_user(username='Third')
        Follow.objects.create(user_id=self.user.id,
                              author_id=following_author.id)
        second_post = Post.objects.create(
            author=following_author,
            text='Очень интересный тестовый пост достаточной длины',
        )
        self.authorized_client.force_login(second_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(second_post, response.context['page_obj'])

    def test_user_cant_subscribe_to_itself(self):
        """Пользователь не может подписаться на самого себя."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context['page_obj'])
