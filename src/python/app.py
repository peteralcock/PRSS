from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from celery import Celery
import feedparser

# Initialize Flask app
app = Flask(__name__)

# Configure app with database and Celery settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pr_monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Initialize Celery
def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Database models
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    published_at = db.Column(db.String(100), nullable=True)
    hashtags = db.Column(db.String(200), nullable=True)

# Celery task for fetching new entries
@celery.task
def fetch_entries(feed_id):
    feed = Feed.query.get(feed_id)
    feed_data = feedparser.parse(feed.url)
    for entry in feed_data.entries:
        new_entry = Entry(
            title=entry.title,
            url=entry.link,
            content=entry.get('summary', ''),
            published_at=entry.get('published', ''),
            hashtags='#'.join([tag['term'] for tag in entry.tags]) if 'tags' in entry else ''
        )
        db.session.add(new_entry)
    db.session.commit()

# API to get all feeds
@app.route('/api/feeds', methods=['GET'])
def get_feeds():
    feeds = Feed.query.all()
    return jsonify([{'title': feed.title, 'url': feed.url, 'category': feed.category} for feed in feeds])

# API to add a new feed
@app.route('/api/feeds', methods=['POST'])
def add_feed():
    data = request.json
    new_feed = Feed(title=data['title'], url=data['url'], category=data['category'])
    db.session.add(new_feed)
    db.session.commit()
    
    # Schedule task to fetch entries from the new feed
    fetch_entries.delay(new_feed.id)
    
    return jsonify({'success': True, 'feed': {'title': new_feed.title, 'url': new_feed.url, 'category': new_feed.category}}), 201

# API to get all entries
@app.route('/api/entries', methods=['GET'])
def get_entries():
    entries = Entry.query.all()
    return jsonify([{
        'title': entry.title,
        'url': entry.url,
        'content': entry.content,
        'published_at': entry.published_at,
        'hashtags': entry.hashtags
    } for entry in entries])

# Initialize the database (only run once)
# @app.before_first_request
# def create_tables():
#   db.create_all()

# Main entry point to run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

