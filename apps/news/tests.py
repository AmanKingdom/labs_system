from django.test import TestCase


class APITest(TestCase):

    def test_post_api(self):
        import requests
        url = 'http://127.0.0.1:8000'
        data = {'title': 'test_title', 'content': 'test_content',}
        r = requests.post(url, data=data)
        print(r.text)
