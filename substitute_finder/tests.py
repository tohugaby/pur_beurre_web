from django.test import TestCase
from django.urls import reverse

# Create your tests here.

# Home page
# returns 200


class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('substitute_finder:index'))
        self.assertEqual(response.status_code, 200)

# Account Page
# returns 200
# redirect to login if user is not authenticated


class AccountPageTestCase(TestCase):
    fixtures = ['substitute_finder.json']

    def test_account_page_when_authenticated(self):
        self.client.login(
            username='titi@hotmail.com',
            password='tom0123456789')
        response = self.client.get(reverse('substitute_finder:account'), {})
        self.assertEqual(response.status_code, 200)

    def test_account_page_when_not_authenticated(self):
        response = self.client.get(reverse('substitute_finder:account'))
        self.assertEqual(response.status_code, 302)

# Account create page
# returns 200
# returns 302 after post
#  return 200 and errors if  errors in form


class AccountCreatePageTestCase(TestCase):

    def test_account_create_page_get(self):
        response = self.client.get(reverse('substitute_finder:create_account'))
        self.assertEqual(response.status_code, 200)

    def test_account_create_page_post(self):
        form_data = {
            'email': 'toto@titi.fr',
            'username': 'toto',
            'first_name': 'toto',
            'last_name': 'titi',
            'password': 'test'
        }
        response = self.client.post(
            reverse('substitute_finder:create_account'), form_data)
        self.assertEqual(response.status_code, 302)

    def test_account_create_page_post_with_errors(self):
        form_data = {
            'email': 'toto@titi',
            'username': 'toto',
            'first_name': 'toto',
            'last_name': 'titi',
            'password': 'test'
        }
        response = self.client.post(
            reverse('substitute_finder:create_account'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('errors' in response.context.keys())


# Login page
# return 301 if login is ok
# return 200 if there is a mistake in authentication

class LoginPageTestCase(TestCase):
    fixtures = fixtures = ['substitute_finder.json']

    def test_login_page_with_success(self):
        form_data = {'email': 'titi@hotmail.com', 'password': 'tom0123456789'}
        response = self.client.post(
            reverse('substitute_finder:login'), form_data)
        self.assertEqual(response.status_code, 302)

    def test_login_page_with_failure(self):
        form_data = {'email': 'titi@hotmail.com', 'password': 'tom'}
        response = self.client.post(
            reverse('substitute_finder:login'), form_data)
        self.assertEqual(response.status_code, 200)


# Logout page
# redirect to home page

class LogoutTestCase(TestCase):
    def test_logout(self):
        response = self.client.get(reverse('substitute_finder:logout'))
        self.assertEqual(response.status_code, 302)
