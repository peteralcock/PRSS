# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from celery import Celery
import feedparser
from datetime import datetime
import re

app = Flask(__name__, static_folder='public')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pr_monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Models
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    hashtags = db.Column(db.String(200))

# Celery tasks
@celery.task
def fetch_feed(feed_id):
    feed = Feed.query.get(feed_id)
    if not feed:
        return

    parsed_feed = feedparser.parse(feed.url)
    
    for entry in parsed_feed.entries:
        existing_entry = Entry.query.filter_by(url=entry.link).first()
        
        if existing_entry:
            existing_entry.title = entry.title
            existing_entry.content = entry.summary
            existing_entry.published_at = datetime(*entry.published_parsed[:6])
        else:
            new_entry = Entry(
                feed_id=feed.id,
                title=entry.title,
                url=entry.link,
                content=entry.summary,
                published_at=datetime(*entry.published_parsed[:6]),
                hashtags=generate_hashtags(entry.title + " " + entry.summary)
            )
            db.session.add(new_entry)
        
    db.session.commit()

def generate_hashtags(text):
    words = re.findall(r'\w+', text.lower())
    return ' '.join(f'#{word}' for word in set(words) if len(word) > 5)

@celery.task
def schedule_feed_fetching():
    feeds = Feed.query.all()
    for feed in feeds:
        fetch_feed.delay(feed.id)

# API routes
@app.route('/api/feeds', methods=['GET', 'POST'])
def handle_feeds():
    if request.method == 'GET':
        feeds = Feed.query.all()
        return jsonify([{'id': f.id, 'title': f.title, 'url': f.url, 'category': f.category} for f in feeds])
    elif request.method == 'POST':
        data = request.json
        new_feed = Feed(title=data['title'], url=data['url'], category=data['category'])
        db.session.add(new_feed)
        db.session.commit()
        fetch_feed.delay(new_feed.id)
        return jsonify({'success': True, 'id': new_feed.id})

@app.route('/api/entries')
def get_entries():
    entries = Entry.query.order_by(Entry.published_at.desc()).limit(20).all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'url': e.url,
        'content': e.content,
        'published_at': e.published_at.isoformat(),
        'hashtags': e.hashtags
    } for e in entries])

@app.route('/api/search')
def search_entries():
    query = request.args.get('q', '')
    entries = Entry.query.filter(
        (Entry.title.like(f'%{query}%')) | (Entry.content.like(f'%{query}%'))
    ).all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'url': e.url,
        'content': e.content,
        'published_at': e.published_at.isoformat(),
        'hashtags': e.hashtags
    } for e in entries])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# celery_config.py
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'fetch-feeds-every-hour': {
        'task': 'app.schedule_feed_fetching',
        'schedule': crontab(minute=0, hour='*')
    },
}
