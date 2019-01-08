"""
Module to test all comments views
"""
from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient

from substitute_finder.models import CustomUser, Product, Comment


class CommentViewTestCase(TestCase):
    """
    Test all views relative to comments
    """
    fixtures = ['test_permissions.json', 'test_users.json', 'test_categories.json', 'test_products.json']

    def setUp(self):
        self.comment_change_permission = Permission.objects.get(codename='can_change_all_commments')
        self.comment_delete_permission = Permission.objects.get(codename='can_delete_all_comments')

        self.user_password = 'test'

        self.admin = CustomUser.objects.get(email='admin@test.fr')
        self.admin.set_password(self.user_password)
        self.admin.save()

        self.user = CustomUser.objects.get(email='user@test.fr')
        self.user.set_password(self.user_password)
        self.user.save()

        self.second_user = CustomUser.objects.get(email='another_user@test.fr')
        self.second_user.set_password(self.user_password)
        self.second_user.save()

        self.product = Product.objects.first()
        self.comment = Comment.objects.create(comment_text='commentaire de test', user=self.user, product=self.product)
        self.nb_comments = Comment.objects.count()
        self.client = APIClient()

    def test_comment_list_view_when_not_authenticated(self):
        """
        Test comment list view when not authenticated
        """
        response = self.client.get(f'/product/{self.product.pk}/comments')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Saisir un nouveau commentaire")

    def test_comment_list_view_when_authenticated(self):
        """
        Test comment list view when authenticated
        """
        self.client.login(username=self.user.email, password=self.user_password)
        response = self.client.get(f'/product/{self.product.pk}/comments')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saisir un nouveau commentaire")

    def test_comment_api_list_view(self):
        """
        Test comment list api view
        """
        response = self.client.get(f'/api/products/{self.product.pk}/comments-list/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "commentaire de test")

    def test_comment_create_api_view_when_authenticated(self):
        """
        Test comment creation api view when authenticated.
        """

        user_login = self.client.login(username=self.user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = '/api/comments/'
        response = self.client.post(url, data={'comment_text': 'test de commentaire', 'product': self.product.pk},
                                    format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.nb_comments + 1, Comment.objects.all().count())

    def test_comment_create_api_view_when_not_authenticated(self):
        """
        Test comment creation api view when not authenticated.
        """
        self.client.login()
        url = '/api/comments/'
        response = self.client.post(url, data={'comment_text': 'test de commentaire', 'product': self.product.pk},
                                    format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"user":["Ce champ ne peut \xc3\xaatre nul."]}')
        self.assertEqual(self.nb_comments, Comment.objects.all().count())

    def test_comment_update_view_when_authenticated(self):
        """
        Test comment update view when authenticated and when request user is comment user.
        """
        user_login = self.client.login(username=self.user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        response = self.client.patch(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment_text, 'test de commentaire modifié')

    def test_comment_update_view_when_admin(self):
        """
        Test comment update view when authenticated as an admin.
        """
        user_login = self.client.login(username=self.admin.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        response = self.client.patch(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment_text, 'test de commentaire modifié')

    def test_comment_update_view_when_authenticated_with_different_user_as_comment_user(self):
        """
        Test comment update view when authenticated and when request user is not comment user.
        """
        user_login = self.client.login(username=self.second_user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        response = self.client.patch(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content,
                         b'{"detail":"Vous n\'avez pas les droits '
                         b'pour mettre \xc3\xa0 jour ou supprimer ce commentaire"}')
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.comment_text, 'test de commentaire modifié')

    def test_comment_update_view_when_authenticated_with_custom_perm(self):
        """
        Test comment update view when authenticated and when request user is not comment user.
        """

        self.second_user.user_permissions.add(self.comment_change_permission)
        self.second_user.save()
        user_login = self.client.login(username=self.second_user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        response = self.client.patch(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment_text, 'test de commentaire modifié')

    def test_comment_update_view_when_not_authenticated(self):
        """
        Test comment update view when not authenticated.
        """
        url = f'/api/comments/{self.comment.pk}/'
        response = self.client.patch(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 403)
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.comment_text, 'test de commentaire modifié')

    def test_comment_delete_view_when_authenticated(self):
        """
        Test comment deletion view.
        """
        user_login = self.client.login(username=self.user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        # url = f'/comment/{self.comment.pk}/delete'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.nb_comments - 1, Comment.objects.all().count())

    def test_comment_delete_view_when_authenticated_with_custom_perm(self):
        """
        Test comment deletion view.
        """
        self.second_user.user_permissions.add(self.comment_delete_permission)
        user_login = self.client.login(username=self.second_user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        # url = f'/comment/{self.comment.pk}/delete'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.nb_comments - 1, Comment.objects.all().count())

    def test_comment_delete_view_when_admin(self):
        """
        Test comment deletion view.
        """
        user_login = self.client.login(username=self.admin.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        # url = f'/comment/{self.comment.pk}/delete'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.nb_comments - 1, Comment.objects.all().count())

    def test_comment_delete_view_when_authenticated_with_different_user_as_comment_user(self):
        """
        Test comment deletion view.
        """
        user_login = self.client.login(username=self.second_user.email, password=self.user_password)
        self.assertTrue(user_login)
        url = f'/api/comments/{self.comment.pk}/'
        # url = f'/comment/{self.comment.pk}/delete'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content,
                         b'{"detail":"Vous n\'avez pas les droits '
                         b'pour mettre \xc3\xa0 jour ou supprimer ce commentaire"}')
        self.assertEqual(self.nb_comments, Comment.objects.all().count())

    def test_comment_delete_view_when_not_authenticated(self):
        """
        Test comment deletion view.
        """
        url = f'/api/comments/{self.comment.pk}/'
        # url = f'/comment/{self.comment.pk}/delete'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.nb_comments, Comment.objects.all().count())
