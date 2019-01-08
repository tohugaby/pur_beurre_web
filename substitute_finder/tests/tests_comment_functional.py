"""
Comment functional tests.
"""
from django.contrib.auth.models import Permission
from selenium.common.exceptions import NoSuchElementException

from substitute_finder.models import CustomUser, Product, Comment
from substitute_finder.tests.test_helpers import CustomStaticLiveServerTestCase


class CommentUserInterfaceTestCase(CustomStaticLiveServerTestCase):
    """
    Live tests for user interface.
    """
    fixtures = ['test_users.json', 'test_categories.json', 'test_products.json']

    def test_add_comment_when_authenticated(self):
        """
        Test comment creation
        """
        product = Product.objects.first()
        self.client.login(username="user@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#id_comment_text").is_displayed())
        nb_card = len(self.browser.find_elements_by_css_selector('.card'))

        comment_text_field = self.get_element('#id_comment_text')
        submit_button = self.get_element('#add-form button')
        comment_text_field.send_keys("youpi")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element(".card").is_displayed())

        new_nb_card = len(self.browser.find_elements_by_css_selector('.card'))

        self.assertEqual(nb_card + 1, new_nb_card)

    def test_cannot_add_comment_when_not_authenticated(self):
        """
        Test that unauthenticated users can't create comment.
        """
        product = Product.objects.first()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        with self.assertRaises(NoSuchElementException):
            self.get_element("#id_comment_text")

    def test_change_comment_when_authenticated(self):
        """
        Test that authenticated user with rights can change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        self.client.login(username="user@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        update_icon = self.get_element("#comment_%s .comment-update" % comment.pk)
        update_icon.click()
        self.wait.until(lambda driver: self.get_element("#comment_%s #id_comment_text" % comment.pk).is_displayed())
        comment_text_field = self.get_element("#comment_%s #id_comment_text" % comment.pk)
        comment_update_button = self.get_element("#comment_%s button.btn" % comment.pk)
        comment_text_field.send_keys("youpi")
        comment_update_button.click()
        self.assertEqual("youpiyoupi", Comment.objects.get(pk=comment.pk).comment_text)

    def test_change_comment_when_authenticated_with_custom_perm(self):
        """
        Test that authenticated user with rights can change a comment even if he's not comment owner.
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")

        another_user = CustomUser.objects.get(email="another_user@test.fr")
        comment_change_permission = Permission.objects.get(codename='can_change_all_commments')
        another_user.user_permissions.add(comment_change_permission)

        self.client.login(username=another_user.email, password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        update_icon = self.get_element("#comment_%s .comment-update" % comment.pk)
        update_icon.click()
        self.wait.until(lambda driver: self.get_element("#comment_%s #id_comment_text" % comment.pk).is_displayed())
        comment_text_field = self.get_element("#comment_%s #id_comment_text" % comment.pk)
        comment_update_button = self.get_element("#comment_%s button.btn" % comment.pk)
        comment_text_field.send_keys("youpi")
        comment_update_button.click()
        self.assertEqual("youpiyoupi", Comment.objects.get(pk=comment.pk).comment_text)

    def test_change_comment_when_admin(self):
        """
        Test that admin can change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        self.client.login(username="admin@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        update_icon = self.get_element("#comment_%s .comment-update" % comment.pk)
        update_icon.click()
        self.wait.until(lambda driver: self.get_element("#comment_%s #id_comment_text" % comment.pk).is_displayed())
        comment_text_field = self.get_element("#comment_%s #id_comment_text" % comment.pk)
        comment_update_button = self.get_element("#comment_%s button.btn" % comment.pk)
        comment_text_field.send_keys("youpi")
        comment_update_button.click()
        self.assertEqual("youpiyoupi", Comment.objects.get(pk=comment.pk).comment_text)

    def test_cannot_change_comment_when_authenticated_with_different_user_as_comment_user(self):
        """
        Test that unauthenticated user can 't change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")

        self.client.login(username="another_user@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        with self.assertRaises(NoSuchElementException):
            self.get_element("#comment_%s .comment-update" % comment.pk)

    def test_cannot_change_comment_when_not_authenticated(self):
        """
        Test that unauthenticated user can 't change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        with self.assertRaises(NoSuchElementException):
            self.get_element("#comment_%s .comment-update" % comment.pk)

    def test_delete_comment_when_authenticated(self):
        """
        Test that authenticated user with rights can change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        comments_nb = Comment.objects.count()

        self.client.login(username="user@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        delete_icon = self.get_element("#comment_%s .comment-delete" % comment.pk)
        delete_icon.click()

        self.assertEqual(Comment.objects.count(), comments_nb - 1)

    def test_delete_comment_when_authenticated_with_custom_perm(self):
        """
        Test that authenticated user with rights can change a comment even if he's not comment owner.
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        comments_nb = Comment.objects.count()

        another_user = CustomUser.objects.get(email="another_user@test.fr")
        comment_delete_permission = Permission.objects.get(codename='can_delete_all_comments')
        another_user.user_permissions.add(comment_delete_permission)

        self.client.login(username=another_user.email, password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        delete_icon = self.get_element("#comment_%s .comment-delete" % comment.pk)
        delete_icon.click()

        self.assertEqual(Comment.objects.count(), comments_nb - 1)

    def test_delete_comment_when_admin(self):
        """
        Test that admin can change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        comments_nb = Comment.objects.count()

        self.client.login(username="admin@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        delete_icon = self.get_element("#comment_%s .comment-delete" % comment.pk)
        delete_icon.click()

        self.assertEqual(Comment.objects.count(), comments_nb - 1)

    def test_cannot_delete_comment_when_authenticated_with_different_user_as_comment_user(self):
        """
        Test that unauthenticated user can 't change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")

        self.client.login(username="another_user@test.fr", password="test")
        cookie = self.client.cookies['sessionid']

        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.browser.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.browser.refresh()
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        with self.assertRaises(NoSuchElementException):
            self.get_element("#comment_%s .comment-delete" % comment.pk)

    def test_cannot_delete_comment_when_not_authenticated(self):
        """
        Test that unauthenticated user can 't change a comment
        """
        product = Product.objects.first()
        user = CustomUser.objects.get(email="user@test.fr")
        comment = Comment.objects.create(user=user, product=product, comment_text="youpi")
        self.browser.get(f"{self.live_server_url}/product/{product.pk}/comments")
        self.wait.until(lambda driver: self.get_element("#comment_%s" % comment.pk).is_displayed())

        with self.assertRaises(NoSuchElementException):
            self.get_element("#comment_%s .comment-delete" % comment.pk)
