from django.test import SimpleTestCase
from users.templatetags import custome_filters

class GetItemFilterTest(SimpleTestCase):
    def test_key_exists_in_dict(self):
        data = {'name': 'queen'}
        result = custome_filters.get_item(data, 'name')
        self.assertEqual(result, 'queen')

    def test_key_missing_in_dict(self):
        data = {'name': 'queen'}
        result = custome_filters.get_item(data, 'age')
        self.assertIsNone(result)

    def test_input_not_a_dict(self):
        data = ['not', 'a', 'dict']
        result = custome_filters.get_item(data, 'key')
        self.assertIsNone(result)
