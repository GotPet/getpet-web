from django.test import SimpleTestCase


class ApiSchemaTest(SimpleTestCase):

    def test_api_schema(self):
        response = self.client.get('/api/?format=openapi')
        self.assertEqual(response.status_code, 200)
