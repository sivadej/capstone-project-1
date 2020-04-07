import os
from unittest import TestCase

os.environ['DATABASE_URL'] = "postgresql:///w2wtest"
from app import app
app.config['WTF_CSRF_ENABLED'] = False

class GeneralTests(TestCase):

	def setUp(self):
		self.client = app.test_client()
	
	def tearDown(self):
		resp = super().tearDown()
		return resp

	def test_root_redirects(self):
		with self.client as c:
			resp = c.get('/')
			self.assertEqual(resp.status_code, 302)
	
	def test_root_redirect_search_view(self):
		with self.client as c:
			resp = c.get('/', follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertIn('What-2-Watch', str(resp.data))
			self.assertIn('Year From', str(resp.data))
			self.assertIn('Register', str(resp.data))

	def test_root_redirect_anon(self):
		# anon user should not see User-specific nav links
		with self.client as c:
			resp = c.get('/', follow_redirects=True)
			self.assertEqual(resp.status_code, 200)
			self.assertNotIn('Account', str(resp.data))
			self.assertNotIn('My Lists', str(resp.data))
			self.assertNotIn('Logout', str(resp.data))