from django.test import TestCase, SimpleTestCase
from . import services

# Create your tests here.

class PagesTests(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)

    def test_about_page_status_code(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)


class ServicesTests(TestCase):
    def test_get_investment_suggestion_ZBRA(self):
        suggestion = services.get_investment_suggestion('ZBRA',discount=0.025,margin=0.15)
        self.assertEqual(suggestion.iloc[0].lasteps, 10.08)
