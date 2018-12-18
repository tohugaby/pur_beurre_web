"""
Module to test all comments views
"""

from django.test import TestCase

from substitute_finder.models import CustomUser, Product, Comment


class CommentViewTestCase(TestCase):
    """
    Test all views relative to comments
    """
    fixtures = ['test_data_short', ]

    def setUp(self):
        self.user = CustomUser.objects.first()
        self.user.set_password('test')
        self.user.save()
        self.product = Product.objects.first()
        self.comment = Comment.objects.create(comment_text='commentaire de test', user=self.user, product=self.product)
        self.nb_comments = Comment.objects.count()

    def test_comment_list_view(self):
        """
        Test comment list view
        """
        response = self.client.get(f'/product/{self.product.pk}/comments')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "commentaire de test")

    def test_comment_create_view(self):
        """
        Test comment creation view.
        """
        user_login = self.client.login(username=self.user.email, password='test')
        self.assertTrue(user_login)
        url = f'/product/{self.product.pk}/comments/create'
        response = self.client.post(url, data={'comment_text': 'test de commentaire'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.nb_comments + 1, Comment.objects.all().count())

    def test_comment_update_view(self):
        """
        Test comment creation view.
        """
        user_login = self.client.login(username=self.user.email, password='test')
        self.assertTrue(user_login)
        url = f'/comment/{self.comment.pk}/update'
        response = self.client.post(url, data={'comment_text': 'test de commentaire modifié'})
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment_text, 'test de commentaire modifié')


    def test_comment_delete_view(self):
        """
        Test comment deletion view.
        """
        user_login = self.client.login(username=self.user.email, password='test')
        self.assertTrue(user_login)
        url = f'/comment/{self.comment.pk}/delete'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.nb_comments - 1, Comment.objects.all().count())
