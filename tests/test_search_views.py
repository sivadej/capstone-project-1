import os
from unittest import TestCase
from models import db, connect_db, User, Watchlist, SavedMovie, Watchlist_Movie

os.environ['DATABASE_URL'] = "postgresql:///w2wtest"
from app import app, login_manager
app.config['WTF_CSRF_ENABLED'] = False

class AnonSearchTests(TestCase):

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()
		self.client = app.test_client()
	
	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp

	def test_anon_search_form(self):
		with self.client as c:
			resp = c.get('/search')
			self.assertEqual(resp.status_code, 200)
			self.assertIn('What-2-Watch', str(resp.data))
			self.assertIn('Year From', str(resp.data))
			self.assertIn('Register', str(resp.data))
	
	def test_anon_search_result(self):
		# should redirect on valid search form submit
		with self.client as c:
			resp = c.post('/search', data={
				'audio': 'English',
				'subs': 'Spanish', 
				'year_from' : '1900', 
				'year_to':'2000', 
				'filter_movie':True, 
				'filter_series':True
			})
			self.assertEqual(resp.status_code, 302)
	
	def test_anon_invalid_search(self):
		# should return to search page on invalid form
		with self.client as c:
			resp = c.post('/search', data={
				'audio': 'xxxxxx',
				'subs': 'xxxxxx', 
				'year_from' : '1900', 
				'year_to':'2000', 
				'filter_movie':True, 
				'filter_series':True
			})
			self.assertEqual(resp.status_code, 200)
			self.assertIn('Search below', str(resp.data))
			self.assertIn('year_to', str(resp.data))
			self.assertIn('<option', str(resp.data))