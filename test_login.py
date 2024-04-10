import unittest
from app import app

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_login_correct_credentials(self):
        response = self.app.post('/login', data={'username': 'Admin', 'password': '123456'}, follow_redirects=True)
        self.assertIn(b'login', response.data)

    def test_login_incorrect_credentials(self):
        response = self.app.post('/login', data={'username': 'xu', 'password': '333'}, follow_redirects=True)
        self.assertIn(b'id', response.data)




    

if __name__ == '__main__':
    unittest.main()
