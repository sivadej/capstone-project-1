import os
from unittest import TestCase
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie

os.environ['DATABASE_URL'] = "postgresql:///w2wtest"
from app import app, login_manager
app.config['WTF_CSRF_ENABLED'] = False

class LoggedInViewTests(TestCase):

	@login_manager.request_loader
	def load_user_from_request(request):
		user = User.query.first()
		return user

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()

		self.client = app.test_client()

		self.testuser = User.register('UserView2', 'test1@test.com', 'password123')
		self.testuser.id = 7894
		db.session.commit()
	
	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp

	def test_profile_view(self):
		with self.client as c:
			resp = c.post('/login', data={
				'username': 'UserView2', 'password': 'password123'
			}, follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertIn('UserView2', str(resp.data))

	def test_invalid_login_submit(self):
		with self.client as c:
			resp = c.post('/login', data={
				'username': 'UserView2', 'password': '12345678'
			}, follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertIn('Invalid login', str(resp.data))

	def test_watchlist_view_auth(self):
		with self.client as c:
			resp = c.get('/my_lists', follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertIn('My Watchlists', str(resp.data))
	
	def test_edit_watchlist_view_auth(self):
		with self.client as c:
			resp = c.get('/user/7894/edit', follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertIn('Edit Account Details', str(resp.data))
			self.assertIn('UserView2', str(resp.data))
	
	def test_edit_other_watchlist_unauth(self):
		with self.client as c:
			resp = c.get('/user/999/edit', follow_redirects=True)
			self.assertEqual(resp.status_code, 403)


class AnonViewTests(TestCase):

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()

		self.client = app.test_client()
	
	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp
	
	def test_login_view(self):
		with self.client as c:
			resp = c.get('/login')
			self.assertIn('User Name', str(resp.data))
			self.assertIn('Password', str(resp.data))
	
	def test_profile_unauth(self):
		with self.client as c:
			resp = c.get('/profile', follow_redirects=True)
			self.assertEqual(resp.status_code, 401)
	
	def test_watchlist_view_unauth(self):
		with self.client as c:
			resp = c.get('/my_lists', follow_redirects=True)
			self.assertEqual(resp.status_code, 401)
	

class UserRegistrationViewsTests(TestCase):

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()

		self.client = app.test_client()
	
	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp

	def test_valid_registration_form(self):
		self.client = app.test_client()
		with self.client as c:
			resp = c.post('/register', data={
				'username': 'NewUserReg', 'email':'new@user.com', 'password': 'abcdefg123'
			})
			self.assertEqual(resp.status_code, 302)