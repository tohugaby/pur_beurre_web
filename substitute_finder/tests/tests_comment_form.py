"""
Module to test comment forms
"""
from django.test import TestCase

from substitute_finder.forms import CreateOrUpdateCommentForm
from substitute_finder.models import Comment, CustomUser, Product


class CommentFormTestCase(TestCase):
    """
    Test Comment forms.
    """
    fixtures = ['test_data_short.json', ]

    def test_comment_creation_form(self):
        """
        Test comment creation form.
        """
        nb_comments = Comment.objects.count()
        comment_form = CreateOrUpdateCommentForm({
            'comment_text': 'test'
        })
        comment = comment_form.save(commit=False)
        comment.user = CustomUser.objects.first()
        comment.product = Product.objects.first()
        comment_form.save()
        self.assertEqual(Comment.objects.count(), nb_comments + 1)
