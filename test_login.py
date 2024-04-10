
import unittest
from app import app

class TestLogin(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app = Flask(__name__, template_folder='../templates')
        app.config.from_object(self)
        from app import db
        db.init_app(app)
        return app

    def setUp(self):
        from app import db
        db.create_all()

    def tearDown(self):
        from app import db
        db.session.remove()
        db.drop_all()

    def test_login_correct_credentials(self):
        response = self.client.post('/login', data={'username': 'Admin', 'password': '123456', 'userId': '1001'}, follow_redirects=True)
        self.assertIn(b'login', response.data)

    def test_login_incorrect_credentials(self):
        response = self.client.post('/login', data={'username': 'xu', 'password': '333', 'userId': '2002'}, follow_redirects=True)
        self.assertIn(b'id', response.data)

if __name__ == '__main__':
    unittest.main()
