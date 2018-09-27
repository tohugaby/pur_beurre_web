from pprint import pprint

import selenium.webdriver.support.ui as ui
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from substitute_finder.models import CustomUser


class UserInterfaceTestCase(StaticLiveServerTestCase):
    fixtures = ['test_data_custom_user.json', 'selenium.json']

    @classmethod
    def setUpClass(cls):
        super(UserInterfaceTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()
        cls.wait = ui.WebDriverWait(cls.browser, 1000)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(UserInterfaceTestCase, cls).tearDownClass()

    # TODO: add a check server is live method

    @classmethod
    def get_element(cls, css_selector: str):
        """
        A shortcut to get an html element by css selector.
        :param css_selector: searched css selector
        :type css_selector: str
        """
        return cls.browser.find_element_by_css_selector(css_selector)

    def test_header_form(self):
        """
        Test a search using header form.
        """
        self.browser.get(self.live_server_url)

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))

    def test_navbar_form(self):
        """
        Test a search using navbar form.
        """
        self.browser.get(self.live_server_url)
        self.wait.until(lambda driver: self.get_element(".navbar-form").is_displayed())
        search_field = self.get_element(".navbar-form #id_product")
        search_field.send_keys("coca")
        search_field.send_keys(Keys.ENTER)
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())
        self.assertEqual(self.browser.current_url, "%s/search" % self.live_server_url)
        self.assertTrue(self.get_element(".product-card"))

    def test_login_form(self):
        """
        Test user login.
        """
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

        self.assertEqual(session.get_decoded()['_auth_user_id'], str(user.pk))
        self.assertEqual(self.browser.current_url, "%s/" % self.live_server_url)
        self.assertTrue(self.get_element("header form #id_product"))

    def test_login_form_wrong_password(self):
        """
        Test user login.
        """
        self.browser.get("%s/login" % self.live_server_url)
        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("test@test.fr")
        password_field.send_keys("wrong")
        submit_button.click()
        
        self.assertEqual(self.browser.current_url, "%s/login" % self.live_server_url)
        self.assertTrue(self.get_element(".alert"))


    # TODO:  test create account,

    def test_logout_form(self):
        """
        Test user logout.
        """
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

    def test_visit_product_page(self):
        """
        Test product page.
        """
        self.browser.get(self.live_server_url)

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())

        card_link = self.get_element(".product-card a.card-body")
        card_link.click()

        product_header = self.get_element(".producthead")
        self.assertTrue(product_header)

        product_id = self.get_element(".producthead .container .row .col").get_attribute("id")

        cards = self.browser.find_elements_by_css_selector(".product-card")
        cards_id = [card.get_attribute("id") for card in cards]

        self.assertNotIn(product_id, cards_id)

    def test_add_to_favorites(self):
        """
        Test addition of product to favorites and visit favorites page.
        """
        self.browser.get("%s/login" % self.live_server_url)

        self.wait.until(lambda driver: self.get_element("#id_email").is_displayed())
        email_field = self.get_element("#id_email")
        password_field = self.get_element("#id_password")
        submit_button = self.get_element("form button")
        email_field.send_keys("test@test.fr")
        password_field.send_keys("test")
        submit_button.click()

        self.wait.until(lambda driver: self.get_element("header form").is_displayed())
        search_field = self.get_element("header form #id_product")
        submit_button = self.get_element("header form button")
        search_field.send_keys("coca")
        submit_button.click()
        self.wait.until(lambda driver: self.get_element("#relevant_products").is_displayed())

        product_card = self.get_element(".product-card")
        product_card_id = product_card.get_attribute("id")
        card_add_to_favorites_link = self.get_element(".product-card .card-footer a")
        card_add_to_favorites_link.click()

        carot = self.get_element(".header-logo").find_element_by_xpath('../..')
        carot.click()
        self.assertIn("/favorites", self.browser.current_url)
        cards = self.browser.find_elements_by_css_selector(".product-card")
        cards_id = [card.get_attribute("id") for card in cards]
        self.assertIn(product_card_id, cards_id)
