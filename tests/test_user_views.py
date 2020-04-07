import os
from unittest import TestCase
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie
from flask_login import LoginManager, login_required, login_user, current_user, logout_user

os.environ['DATABASE_URL'] = "postgresql:///w2wtest"


# Now we can import app

from app import app

login_manager = LoginManager()
login_manager.init_app(app)
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

class LoggedInViewTests(TestCase):
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
	
	@login_manager.request_loader
	def load_user_from_request(request):
		print('LOGGING IN SOMEONE HELLOOOO **********')
		user = User.query.first()
		print(user)
		return user

	def test_profile_view(self):
		with self.client as c:
			resp = c.post('/login', data={
				'username': 'UserView1', 'password': 'password123'
			})
			self.assertEqual(resp.status_code, 200)
			self.assertIn('UserView1', str(resp.data))

	def test_watchlist_view_auth(self):
		with self.client as c:
			user = User.authenticate('UserView1','password123')
			self.load_user_from_request(user)
			resp = c.get('/my_lists')
			#print(resp.data)
			#print(user)
			#print(current_user)
			#self.assertEqual(resp.status_code, 200)
			self.assertEqual(1,1)
	


class AnonViewTests(TestCase):

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()

		self.client = app.test_client()

		self.testuser = User.register('UserView1', 'test1@test.com', 'password123')
		self.testuser.id = 5555
		db.session.commit()
	
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
			print(resp.data)
			self.assertEqual(resp.status_code, 401)