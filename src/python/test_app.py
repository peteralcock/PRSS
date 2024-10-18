import pytest
from app import app, db, Feed, Entry, fetch_feed, generate_hashtags

@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    # Insert a sample feed for testing
    feed = Feed(title='Sample Feed', url='http://example.com/rss', category='news')
    db.session.add(feed)
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()


import pytest
from app import app, db, Feed, Entry, fetch_feed, generate_hashtags
from flask import jsonify

# Create a test client fixture
@pytest.fixture(scope='module')
def test_client():
    flask_app = app
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_pr_monitoring.db'
    flask_app.config['TESTING'] = True

    testing_client = flask_app.test_client()

    # Establish an application context
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # testing happens here!

    # Clean up after tests
    ctx.pop()

# Fixture to initialize the database
@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    # Insert a sample feed for testing
    feed = Feed(title='Sample Feed', url='http://example.com/rss', category='news')
    db.session.add(feed)
    db.session.commit()

    yield db  # testing happens here!

    db.drop_all()

### Test cases ###

# Test the /api/feeds endpoint (GET)
def test_get_feeds(test_client, init_database):
    response = test_client.get('/api/feeds')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1  # Expecting one feed added from init_database
    assert data[0]['title'] == 'Sample Feed'

# Test the /api/feeds endpoint (POST)
def test_post_feed(test_client, init_database):
    new_feed = {
        'title': 'New Feed',
        'url': 'http://newfeed.com/rss',
        'category': 'tech'
    }
    response = test_client.post('/api/feeds', json=new_feed)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

    # Check if the new feed was added to the database
    feed = Feed.query.filter_by(title='New Feed').first()
    assert feed is not None
    assert feed.url == 'http://newfeed.com/rss'

# Test the /api/entries endpoint (GET)
def test_get_entries(test_client, init_database):
    # Assuming entries are created by the fetch_feed Celery task
    response = test_client.get('/api/entries')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Should return a list
    assert len(data) == 0  # No entries should exist initially

# Test the /api/search endpoint (GET)
def test_search_entries_no_results(test_client, init_database):
    response = test_client.get('/api/search?q=NonExistent')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0  # No results should match

# Test the generate_hashtags function
def test_generate_hashtags():
    text = "Breaking News: Flask Testing is Awesome"
    hashtags = generate_hashtags(text)
    assert "#breaking" in hashtags
    assert "#flask" in hashtags
    assert "#testing" in hashtags
    assert "#awesome" in hashtags

# Test Celery fetch_feed task
@pytest.mark.celery(result_backend='redis://localhost:6379/0')
def test_fetch_feed(init_database):
    feed = Feed.query.first()
    result = fetch_feed.apply(args=[feed.id])
    assert result.status == "SUCCESS"

# Test the Celery periodic task for fetching all feeds
@pytest.mark.celery(result_backend='redis://localhost:6379/0')
def test_schedule_feed_fetching(init_database):
    from app import schedule_feed_fetching
    result = schedule_feed_fetching.apply()
    assert result.status == "SUCCESS"

# Test /api/search with matching results
def test_search_entries_with_results(test_client, init_database):
    # Create a new entry in the database
    feed = Feed.query.first()
    entry = Entry(
        feed_id=feed.id,
        title="Flask Testing",
        url="http://test.com/article",
        content="This article talks about Flask and Testing.",
        published_at=datetime.now(),
        hashtags=generate_hashtags("Flask Testing")
    )
    db.session.add(entry)
    db.session.commit()

    response = test_client.get('/api/search?q=Flask')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1  # One result should match
    assert data[0]['title'] == "Flask Testing"

# Test error handling for nonexistent feed ID in Celery task
def test_fetch_feed_nonexistent_id():
    result = fetch_feed.apply(args=[9999])  # Nonexistent feed ID
    assert result.result is None  # No result, task should silently handle the error

# Test /api/feeds endpoint with an invalid POST request (missing fields)
def test_post_feed_invalid_data(test_client, init_database):
    invalid_feed = {
        'title': 'Invalid Feed'
        # Missing 'url' and 'category'
    }
    response = test_client.post('/api/feeds', json=invalid_feed)
    assert response.status_code == 400  # Bad request due to missing fields

