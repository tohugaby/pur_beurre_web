from pprint import pprint

import selenium.webdriver.support.ui as ui
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from substitute_finder.models import CustomUser


class SearchFormUserTestCase(StaticLiveServerTestCase):
    fixtures = ['selenium.json']

    @classmethod
    def setUpClass(cls):
        super(SearchFormUserTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()
        cls.wait = ui.WebDriverWait(cls.browser, 1000)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SearchFormUserTestCase, cls).tearDownClass()

    @classmethod
    def get_element(cls, css_selector: str):
        """
        A shortcut to get an html element by css selector.
        :param css_selector: searched css selector
        :type css_selector: str
        """
        return cls.browser.find_element_by_css_selector(css_selector)

    def test_header_form_exists(self):
        self.browser.get(self.live_server_url)
        self.assertIn("Pur Beurre", self.browser.title)
        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))

    def test_navbar_form_exists(self):
        self.browser.get(self.live_server_url)
        self.assertIn("Pur Beurre", self.browser.title)
        self.wait.until(lambda driver: self.get_element(".navbar-form").is_displayed())
        search_field = self.get_element(".navbar-form #id_product")
        search_field.send_keys("coca")
        search_field.send_keys(Keys.ENTER)
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))


class LoginLogoutUserTestCase(StaticLiveServerTestCase):
    fixtures = ['test_data_custom_user.json']

    @classmethod
    def setUpClass(cls):
        super(LoginLogoutUserTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()
        cls.wait = ui.WebDriverWait(cls.browser, 1000)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(LoginLogoutUserTestCase, cls).tearDownClass()

    @classmethod
    def get_element(cls, css_selector: str):
        """
        A shortcut to get an html element by css selector.
        :param css_selector: searched css selector
        :type css_selector: str
        """
        return cls.browser.find_element_by_css_selector(css_selector)

    def test_login_form_exists(self):
        self.browser.get("%s/login" % self.live_server_url)
        self.assertIn("Pur Beurre", self.browser.title)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("test@test.fr")
        password_field.send_keys("test")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("header form #id_product").is_displayed())

        session_id = self.browser.get_cookie("sessionid")['value']

        session = Session.objects.get(pk=session_id)
        user = CustomUser.objects.get(email='test@test.fr')

        self.assertEqual(session.get_decoded()['_auth_user_id'], str(user.pk))
        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertTrue(self.get_element("header form #id_product"))

    def test_logout_form_exists(self):
        self.browser.get("%s/login" % self.live_server_url)

        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("test@test.fr")
        password_field.send_keys("test")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("header form #id_product").is_displayed())

        session_id = self.browser.get_cookie("sessionid")['value']

        session = Session.objects.get(pk=session_id)
        user = CustomUser.objects.get(email='test@test.fr')

        logout_link = self.get_element('.navbar-nav li:nth-child(3) a')

        logout_link.click()

        self.assertIsNone(self.browser.get_cookie("sessionid"))

        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertTrue(self.get_element("header form #id_product"))



# TODO: Missing tests: clic on card, add to favorites, see favorites
