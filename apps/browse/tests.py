from django.test import TestCase


class LogoutTest(TestCase):

    def test_session_is_none_after_logout(self):
        from django.urls import reverse
        response = self.client.get(reverse('browse:logout'))
        pass

