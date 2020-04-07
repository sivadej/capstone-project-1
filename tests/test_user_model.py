import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie

os.environ['DATABASE_URL'] = "postgresql:///w2wtest"

from app import app

class UserModelTests(TestCase):

    def setUp(self):     
        # empty all database entries
        db.session.close()
        db.drop_all()
        db.create_all()

        # create test users. reassign id numbers
        test_user_1 = User.register('TestUser1','test1@test.com','password123')
        test_user_1.id = 1234

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_model(self):
        u = User(username='plaintextTest',email='test@test.com',password='password123')
        self.assertEqual(u.username,'plaintextTest')
        self.assertEqual(u.email,'test@test.com')
        self.assertEqual(u.password,'password123')
        self.assertIsNone(u.id)

    def test_valid_registration(self):
        # test for proper db insertion and bcrypt hash password
        # test for plaintext password NOT stored in db
        u = User.register('test123','test@test.com','password123')
        db.session.commit()
        self.assertIsNotNone(u.id)
        self.assertNotEqual(u.password,'password123')
        self.assertTrue(u.password.startswith('$2b$'))
    
    def test_duplicate_user_reg(self):
        # Users should not be allowed to register with an already existing name 
        with self.assertRaises(IntegrityError) as context:
            dupe = User.register('TestUser1','dupe@email.com','hello321')
            db.session.commit()
    
    def test_invalid_email(self):
        with self.assertRaises(IntegrityError) as context:
            invalid = User.register('TestUser500',None,'hello123456')
            db.session.commit()
    
    def test_invalid_passwd(self):
        with self.assertRaises(ValueError) as context:
            invalid = User.register('Test2020','email@email.net',None)
            db.session.commit()
    
    def test_user_auth(self):
        u = User.register('authMePlease','email@gmail.cn','Hello123!@#')
        db.session.commit()
        should_auth = User.authenticate('authMePlease','Hello123!@#')
        failed_auth = User.authenticate('authMePlease','WrongpasswordKiddo')
        self.assertEqual(should_auth, u)
        self.assertFalse(failed_auth)
    
    def test_user_watchlists(self):
        # test watchlist relationship in user model
        u = User.register('iHaveAwatchlist','email@gmail.cn','password-o-clock')
        u.id = 99999
        db.session.add(Watchlist(title='Test Watchlist',is_shared=False, user_id=u.id))
        db.session.commit()
        print(u.watchlists)
        self.assertEqual(u.watchlists[0].user_id,u.id)
        self.assertEqual(len(u.watchlists),1)