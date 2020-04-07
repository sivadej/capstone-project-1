import os
from unittest import TestCase
from models import db, SavedMovie
os.environ['DATABASE_URL'] = "postgresql:///w2wtest"
from app import app

class MovieTests(TestCase):

	def setUp(self):
		db.session.close()
		db.drop_all()
		db.create_all()
		movie = SavedMovie(netflix_id=12345678, title='Test Saved Movie From Search', video_type='Series')
		db.session.add(movie)
		db.session.commit()
		self.client = app.test_client()

	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp

	def test_movie_model(self):
		# movie should exist alone in database
		movie = SavedMovie.query.first()
		movies = SavedMovie.query.all()
		self.assertEqual(movie.netflix_id,12345678)
		self.assertEqual(movie.title,'Test Saved Movie From Search')
		self.assertEqual(len(movies),1)
	
	def test_invalid_movie_details(self):
		with self.client as c:
			resp = c.get('/movie/99999', follow_redirects=True)
			self.assertEqual(resp.status_code, 404)