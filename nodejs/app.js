// app.js
const express = require('express');
const cors = require('cors');
const { Sequelize, DataTypes } = require('sequelize');
const Queue = require('bull');
const path = require('path');
const FeedParser = require('feedparser');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Database setup
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: 'pr_monitoring.sqlite'
});

// Models
const Feed = sequelize.define('Feed', {
  title: DataTypes.STRING,
  url: DataTypes.STRING,
  category: DataTypes.STRING
});

const Entry = sequelize.define('Entry', {
  feedId: DataTypes.INTEGER,
  title: DataTypes.STRING,
  url: DataTypes.STRING,
  content: DataTypes.TEXT,
  publishedAt: DataTypes.DATE,
  hashtags: DataTypes.STRING
});

// Bull queue setup
const feedQueue = new Queue('feed processing');

// Helper function to generate hashtags
function generateHashtags(text) {
  const words = text.toLowerCase().match(/\b(\w+)\b/g);
  return [...new Set(words)]
    .filter(word => word.length > 5)
    .map(word => `#${word}`)
    .join(' ');
}

// Worker function
feedQueue.process(async (job) => {
  const { feedId } = job.data;
  const feed = await Feed.findByPk(feedId);
  if (!feed) return;

  const res = await axios.get(feed.url);
  const feedparser = new FeedParser();

  feedparser.on('error', (error) => {
    console.error('FeedParser error:', error);
  });

  feedparser.on('readable', async function() {
    let item;
    while (item = this.read()) {
      const [entry, created] = await Entry.findOrCreate({
        where: { url: item.link },
        defaults: {
          feedId: feed.id,
          title: item.title,
          content: item.summary,
          publishedAt: item.pubDate,
          hashtags: generateHashtags(item.title + ' ' + item.summary)
        }
      });

      if (!created) {
        await entry.update({
          title: item.title,
          content: item.summary,
          publishedAt: item.pubDate
        });
      }
    }
  });

  res.data.pipe(feedparser);
});

// API Routes
app.get('/api/feeds', async (req, res) => {
  const feeds = await Feed.findAll();
  res.json(feeds);
});

app.post('/api/feeds', async (req, res) => {
  const feed = await Feed.create(req.body);
  await feedQueue.add({ feedId: feed.id });
  res.json({ success: true, id: feed.id });
});

app.get('/api/entries', async (req, res) => {
  const entries = await Entry.findAll({
    order: [['publishedAt', 'DESC']],
    limit: 20
  });
  res.json(entries);
});

app.get('/api/search', async (req, res) => {
  const { q } = req.query;
  const entries = await Entry.findAll({
    where: {
      [Sequelize.Op.or]: [
        { title: { [Sequelize.Op.like]: `%${q}%` } },
        { content: { [Sequelize.Op.like]: `%${q}%` } }
      ]
    }
  });
  res.json(entries);
});

// Serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Sync database and start server
sequelize.sync().then(() => {
  app.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
  });
});

// Scheduler
setInterval(async () => {
  const feeds = await Feed.findAll();
  for (const feed of feeds) {
    await feedQueue.add({ feedId: feed.id });
  }
}, 3600000); // Run every hour

module.exports = app;
