import unittest

from flask import Flask 
from flask.testing import FlaskClient
from src.main import create_app
from src.models import db_connector, User, Session
import hashlib



class IntegrationAuthTest(unittest.TestCase):
    def setUp(self):
        
        self.app: Flask = create_app('sqlite:///:memory:')
        self.app.config.update({
            'TESTING': True,
        })
        self.app_client: FlaskClient = self.app.test_client()
        

    def tearDown(self):
        with self.app.app_context():
            db_connector.session.remove()
            db_connector.drop_all()
        

    def test_login_user_does_not_exist(self):
        '''
        Test trying to login if there exist no users
        Expect a 401 error
        '''

        user_one: User = User(username='eman', password='skibidi', user_id=1)
        user_two: User = User(username='pep', password='password', user_id=2)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.commit()

        credentials = {'username': 'eman', 'password': 'password'}
        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(response.status_code, 401)

        with self.app.app_context():
            existing_users: list[User] = db_connector.session.execute(db_connector.select(User)).scalars().all()
            existing_sessions: list[Session] = db_connector.session.execute(db_connector.select(Session)).scalars().all()
            self.assertEqual(2, len(existing_users))
            self.assertEqual(0, len(existing_sessions))


    def test_login_user_exist_correct_credentials(self):
        '''
        Test Happy path correct username and password
        and the user exist
        '''
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('pass')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'eman', 'password': 'kek'}
        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(201, response.status_code)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            existing_users: list[User] = db_connector.session.execute(db_connector.select(User)).scalars().all()
            existing_sessions: list[Session] = db_connector.session.execute(db_connector.select(Session)).scalars().all()

            # check to make sure no new entries in the database added for users and that we have a new session
            self.assertEqual(3, len(existing_users))
            self.assertEqual(1, len(existing_sessions))

            # test to make sure session linked to user and session is not null
            self.assertEqual(user_one.user_id, existing_sessions[0].user_id)
            self.assertNotEqual(None, user_one.session)


    def test_login_user_does_not_exist_same_password(self):
        '''
        Test where the username does not exist but there
        exist a user with the same password
        '''
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('password')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'wrongusername', 'password': 'password'}
        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(401, response.status_code)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)

            existing_users: list[User] = db_connector.session.execute(db_connector.select(User)).scalars().all()
            existing_sessions: list[Session] = db_connector.session.execute(db_connector.select(Session)).scalars().all()
            self.assertEqual(3, len(existing_users))
            self.assertEqual(0, len(existing_sessions))

            existing_users.sort(key= lambda user: user.user_id)
            self.assertEqual(user_one, existing_users[0])
            self.assertEqual(user_two, existing_users[1])
            self.assertEqual(user_three, existing_users[2])

    
    def test_login_user_exist_wrong_password(self):
        '''
        Test where the username is correct but the password is correct
        and the user exist
        '''
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('password')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)
        
        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'eman', 'password': 'wrongpassword'}
        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(401, response.status_code)

        users: list[User] = None
        with self.app.app_context():
            # return all rows from user table as a list
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            users = db_connector.session.execute(db_connector.select(User)).scalars().all()
            self.assertEqual(3, len(users))
            users.sort(key=lambda user: user.user_id)
            self.assertEqual(user_one, users[0])
            self.assertEqual(user_two, users[1])
            self.assertEqual(user_three, users[2])
        

    def test_login_correct_credentials_session_exist(self):
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('pass')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'eman', 'password': 'kek'}
        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(201, response.status_code)

        cookie: str = (response.headers['Set-Cookie'])
        session_id: str = cookie.split(';')[0].split('=')[1]

        response = self.app_client.post('/auth/login', json=credentials)
        self.assertEqual(201, response.status_code)

        cookie: str = (response.headers['Set-Cookie'])
        session_id_2: str = cookie.split(';')[0].split('=')[1]

        self.assertEqual(session_id, session_id_2)


        with self.app.app_context():
            users: list[User] = db_connector.session.execute(db_connector.select(User)).scalars().all()
            sessions: list[Session] = db_connector.session.execute(db_connector.select(Session)).scalars().all()

            self.assertEqual(3, len(users))
            self.assertEqual(1, len(sessions))


    def test_register_user(self):
        '''
        Test happy path where the user does not already exist
        '''
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('password')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'emm2145144', 'password': 'Chuye1234!@'}
        result = self.app_client.post('/auth/register', json=credentials)

        self.assertEqual(201, result.status_code)

        with self.app.app_context():
            users: User = db_connector.session.execute(db_connector.select(User)).scalars().all()
            self.assertEqual(4, len(users))


    def test_register_user_already_exist(self):
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('password')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {'username': 'eman', 'password': 'Chuye1234!@'}
        result = self.app_client.post('/auth/register', json=credentials)

        self.assertEqual(400, result.status_code)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            users: list[User] = db_connector.session.execute(db_connector.select(User)).scalars().all()
            users.sort(key=lambda user: user.user_id)
            
            self.assertEqual(3, len(users))
            self.assertEqual(user_one, users[0])
            self.assertEqual(user_two, users[1])
            self.assertEqual(user_three, users[2])

    
    def test_logout_user_logged_in(self):
        hashed_pass_one = self._password_hasher_helper('kek')
        user_one: User = User(username='eman', password= hashed_pass_one, user_id=1)
        hashed_pass_two = self._password_hasher_helper('password')
        user_two: User = User(username='chuye', password= hashed_pass_two, user_id=2)
        hashed_pass_three = self._password_hasher_helper('stop')
        user_three: User = User(username='nibba', password= hashed_pass_three, user_id=3)

        with self.app.app_context():
            db_connector.session.add(user_one)
            db_connector.session.add(user_two)
            db_connector.session.add(user_three)
            db_connector.session.commit()

        credentials = {
                        'username': 'eman',
                        'password': 'kek'
                       }
        
        result = self.app_client.post('/auth/login', json=credentials)
        cookies = (result.headers['Set-Cookie'])
        session_id = cookies.split(';')[0].split('=')[1]
       
        with self.app.app_context():
            current_session: list[Session] = db_connector.session().execute(db_connector.select(Session)).scalars().all()
            self.assertEqual(1, len(current_session))
        
        self.app_client.set_cookie(key='session-id', value=session_id)
        result = self.app_client.delete('/auth/logout')
        self.assertEqual(200, result.status_code)

        with self.app.app_context():
            db_connector.session.add(user_one)
            sessions: Session = db_connector.session.execute(db_connector.select(Session)).scalars().all()
            users: User = db_connector.session.execute(db_connector.select(User)).scalars().all()
            self.assertEqual(0, len(sessions))
            self.assertEqual(None, user_one.session)
            self.assertEqual(3, len(users))


    def _password_hasher_helper(self, password: str) -> str:
        return hashlib.sha256(str.encode(password)).hexdigest()
    

if __name__ == '__main__':
    unittest.main()