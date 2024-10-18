import unittest
import json
from app import app, db, Feed, Entry, fetch_feed, schedule_feed_fetching
from datetime import datetime


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test client using Flask's test client utility
        self.app = app.test_client()
        self.app.testing = True

        # Set up a temporary database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Tear down the temporary database
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_handle_feeds_get(self):
        # Add a sample feed to the database
        with app.app_context():
            new_feed = Feed(title='Test Feed', url='http://test.com/rss', category='Tech')
            db.session.add(new_feed)
            db.session.commit()

        # Send a GET request to the `/api/feeds` route
        response = self.app.get('/api/feeds')
        # Verify the response is a 200 status code
        self.assertEqual(response.status_code, 200)
        # Verify the response contains the feed data
        feeds = json.loads(response.data)
        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0]['title'], 'Test Feed')

    def test_handle_feeds_post(self):
        # Prepare data to be sent in a POST request
        new_feed = {'title': 'Test Feed', 'url': 'http://test.com/rss', 'category': 'Tech'}
        # Send a POST request to the `/api/feeds` route with JSON data
        response = self.app.post('/api/feeds',
                                 data=json.dumps(new_feed),
                                 content_type='application/json')
        # Verify the response is a 200 status code
        self.assertEqual(response.status_code, 200)
        # Verify that the response indicates success
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])

        # Verify the feed is added to the store
        with app.app_context():
            feed = Feed.query.first()
            self.assertIsNotNone(feed)
            self.assertEqual(feed.title, 'Test Feed')

    def test_get_entries(self):
        # Add a sample entry to the database
        with app.app_context():
            new_feed = Feed(title='Test Feed', url='http://test.com/rss', category='Tech')
            db.session.add(new_feed)
            db.session.commit()
            new_entry = Entry(feed_id=new_feed.id, title='Test Entry', url='http://test.com/entry',
                              content='This is a test entry', published_at=datetime.now())
            db.session.add(new_entry)
            db.session.commit()

        # Send a GET request to the `/api/entries` route
        response = self.app.get('/api/entries')
        # Verify the response is a 200 status code
        self.assertEqual(response.status_code, 200)
        # Verify the response contains the entry data
        entries = json.loads(response.data)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['title'], 'Test Entry')

    def test_search_entries(self):
        # Add a sample entry to the database
        with app.app_context():
            new_feed = Feed(title='Test Feed', url='http://test.com/rss', category='Tech')
            db.session.add(new_feed)
            db.session.commit()
            new_entry = Entry(feed_id=new_feed.id, title='Test Entry', url='http://test.com/entry',
                              content='This is a test entry', published_at=datetime.now())
            db.session.add(new_entry)
            db.session.commit()

        # Send a GET request to the `/api/search` route with query
        response = self.app.get('/api/search?q=Test')
        # Verify the response is a 200 status code
        self.assertEqual(response.status_code, 200)
        # Verify the response contains the entry data
        entries = json.loads(response.data)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['title'], 'Test Entry')


if __name__ == '__main__':
    unittest.main()
