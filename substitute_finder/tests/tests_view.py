"""
Test substitute_finder app views.
"""
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.contrib.sessions.models import Session

from substitute_finder.models import Product, CustomUser

# Create your tests here.

# Home page
# returns 200


class IndexViewTestCase(TestCase):
    """
    Test index_view.
    """

    def test_index_page(self):
        """
        Test index view response.
        """
        response = self.client.get(reverse('substitute_finder:index'))
        self.assertEqual(response.status_code, 200)

# Account Page
# returns 200
# redirect to login if user is not authenticated


class AccountViewTestCase(TestCase):
    """
    Test account_view.
    """
    fixtures = ['substitute_finder.json']

    def test_account_page_when_authenticated(self):
        """
        Test access to account page when authenticate.
        """
        self.client.login(
            username='titi@hotmail.com',
            password='tom0123456789')
        response = self.client.get(reverse('substitute_finder:account'), {})
        self.assertEqual(response.status_code, 200)

    def test_account_page_when_not_authenticated(self):
        """
        Test access to account page when not authenticate.
        """
        response = self.client.get(reverse('substitute_finder:account'))
        self.assertEqual(response.status_code, 302)

# Account create page
# returns 200
# returns 302 after post
#  return 200 and errors if  errors in form


class AccountCreateViewTestCase(TestCase):
    """
    Test create_account_view.
    """

    def test_account_create_page_get(self):
        """
        Test access to create account page.
        """
        response = self.client.get(reverse('substitute_finder:create_account'))
        self.assertEqual(response.status_code, 200)

    def test_account_create_page_post(self):
        """
        Test account creation.
        """
        nb_users_before = CustomUser.objects.count()

        form_data = {
            'email': 'toto@titi.fr',
            'username': 'toto',
            'first_name': 'toto',
            'last_name': 'titi',
            'password': 'test'
        }
        response = self.client.post(
            reverse('substitute_finder:create_account'), form_data)

        nb_users_after = CustomUser.objects.count()

        self.assertEqual(response.status_code, 302)
        self.assertGreater(nb_users_after, nb_users_before)

    def test_account_create_page_post_with_errors(self):
        """
        Test account creation when there are errors in form.
        """
        nb_users_before = CustomUser.objects.count()

        form_data = {
            'email': 'toto@titi',
            'username': 'toto',
            'first_name': 'toto',
            'last_name': 'titi',
            'password': 'test'
        }
        response = self.client.post(
            reverse('substitute_finder:create_account'), form_data)
        nb_users_after = CustomUser.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.context.keys())
        self.assertEqual(nb_users_after, nb_users_before)


# Login page
# return 301 if login is ok
# return 200 if there is a mistake in authentication

class LoginViewTestCase(TestCase):
    """
    Test login_view.
    """
    fixtures = fixtures = ['substitute_finder.json']

    def test_login_page_with_success(self):
        """
        Test login success.
        """

        nb_sessions_before = Session.objects.count()

        form_data = {'email': 'titi@hotmail.com', 'password': 'tom0123456789'}
        response = self.client.post(
            reverse('substitute_finder:login'), form_data)

        nb_sessions_after = Session.objects.count()

        self.assertEqual(response.status_code, 302)
        self.assertGreater(nb_sessions_after, nb_sessions_before)

    def test_login_page_with_failure(self):
        """
        Test login failure.
        """

        nb_sessions_before = Session.objects.count()

        form_data = {'email': 'titi@hotmail.com', 'password': 'tom'}
        response = self.client.post(
            reverse('substitute_finder:login'), form_data)

        nb_sessions_after = Session.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(nb_sessions_after, nb_sessions_before)


# Logout page
# redirect to home page

class LogoutViewTestCase(TestCase):
    """
    Test logout_view.
    """
    fixtures = fixtures = ['substitute_finder.json']

    def test_logout(self):
        """
        Test logout success.
        """
        self.client.login(username='titi@hotmail.com', password='tom0123456789')
        nb_sessions_before = Session.objects.count()

        response = self.client.get(reverse('substitute_finder:logout'))

        nb_sessions_after = Session.objects.count()

        self.assertEqual(response.status_code, 302)

        self.assertLess(nb_sessions_after, nb_sessions_before)

# Search page
# POST valid return results or not
# POST invalid
# GET return last search else redirect to home page


class SearchViewTestCase(TestCase):
    """
    Test search_view.
    """

    fixtures = ['test_data_custom_user.json', 'selenium.json']

    def test_post_with_results(self):
        """
        Test post on search view that returns many resulsts.
        """
        response = self.client.post(reverse('substitute_finder:search'), {'product': 'coca'})
        self.assertEqual(response.status_code, 200)
        results = response.context['products'].object_list
        self.assertGreater(len(results), 0)

    def test_post_with_one_result(self):
        """
        Test post on search view that returns one resulst.
        """
        response = self.client.post(reverse('substitute_finder:search'), {'product': 'CocaCola'})
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        product = response.context['product']
        self.assertEqual(len(products), 0)
        self.assertIsInstance(product, Product)

    def test_post_with_no_results(self):
        """
        Test post on search view that returns no resulsts.
        """
        response = self.client.post(reverse('substitute_finder:search'), {'product': 'tarte au fromage'})
        self.assertEqual(response.status_code, 200)
        results = response.context['products'].object_list
        messages = list(response.context['messages'])
        self.assertEqual(len(results), 0)
        self.assertEqual(len(messages), 1)

    def test_post_invalid(self):
        """
        Test invalid post on search view.
        """
        response = self.client.post(reverse('substitute_finder:search'), {'product': ''})
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_get_with_previous_search(self):
        """
        Test get on search view that returns resulsts from last search.
        """
        previous_response = self.client.post(reverse('substitute_finder:search'), {'product': 'coca'})
        previous_results = previous_response.context['products'].object_list
        response = self.client.get(reverse('substitute_finder:search'))
        results = response.context['products'].object_list
        self.assertEqual(len(previous_results), len(results))

    def test_get_with_no_previous_search(self):
        """
        Test get on search view that redirect to home because there is no last search.
        """
        response = self.client.get(reverse('substitute_finder:search'))
        self.assertEqual(response.status_code, 302)


# Product page
# if substitutes exist, it as better nutrition grade
class ProductViewTestCase(TestCase):
    """
    Test product_view.
    """
    fixtures = ['test_data_custom_user.json', 'selenium.json']

    def test_substitute_have_better_nutrition_grade(self):
        """
        If substitutes exist, test they have better nutrition grade than product
        """
        session = self.client.session
        session['last_products'] = [product.pk for product in Product.objects.all()]
        session.save()
        response = self.client.get(reverse('substitute_finder:product', kwargs={'pk': '3174780000288'}))
        self.assertEqual(response.status_code, 200)
        products_grades = [product.nutrition_grade_fr for product in response.context['products']]
        others_grades = [other.nutrition_grade_fr for other in response.context['others']]
        product_grade = response.context['product'].nutrition_grade_fr
        for grade in set(products_grades + others_grades):
            self.assertGreater(product_grade, grade)


# Favorites
# add a favorites to database


class AddFavoritesViewTestCase(TestCase):
    """
    Test add_favorite_view.
    """
    fixtures = ['test_data_custom_user.json', 'selenium.json']

    def test_add_favorites_to_database(self):
        """
        Test adding product to favorites when user is logged.
        """
        product = Product.objects.last()
        nb_user_loving_product_before = product.users.count()
        self.client.login(username='test@test.fr', password='test')
        response = self.client.get(reverse('substitute_finder:add_favorite', kwargs={'pk': product.pk}))
        nb_user_loving_product_after = product.users.count()
        self.assertGreater(nb_user_loving_product_after, nb_user_loving_product_before)

    def test_add_favorites_when_not_logged_in(self):
        """
        Test adding product to favorites when user is logged.
        """
        product = Product.objects.last()
        nb_user_loving_product_before = product.users.count()

        response = self.client.get(reverse('substitute_finder:add_favorite', kwargs={'pk': product.pk}))
        nb_user_loving_product_after = product.users.count()
        self.assertEqual(nb_user_loving_product_after, nb_user_loving_product_before)


class LegalViewTestCase(TestCase):
    """
    Test legal_view.
    """

    def test_legal__page(self):
        """
        Test legal_view response.
        """
        response = self.client.get(reverse('substitute_finder:legal'))
        self.assertEqual(response.status_code, 200)
