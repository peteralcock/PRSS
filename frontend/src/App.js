import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function App() {
  const [feeds, setFeeds] = useState([]);
  const [newFeed, setNewFeed] = useState({ title: '', url: '', category: '' });
  const [entries, setEntries] = useState([]);

  // Fetch Feeds
  useEffect(() => {
    axios.get(`${API_BASE_URL}/feeds`)
      .then((response) => {
        setFeeds(response.data);
      })
      .catch((error) => {
        console.error('There was an error fetching the feeds!', error);
      });
  }, []);

  // Fetch Entries
  useEffect(() => {
    axios.get(`${API_BASE_URL}/entries`)
      .then((response) => {
        setEntries(response.data);
      })
      .catch((error) => {
        console.error('There was an error fetching the entries!', error);
      });
  }, []);

  // Handle form submission to add a new feed
  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post(`${API_BASE_URL}/feeds`, newFeed)
      .then((response) => {
        if (response.data.success) {
          setFeeds([...feeds, newFeed]);
          setNewFeed({ title: '', url: '', category: '' });
        }
      })
      .catch((error) => {
        console.error('There was an error adding the new feed!', error);
      });
  };

  return (
    <div className="App">
      <h1>PR Monitoring Dashboard</h1>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Feed Title"
          value={newFeed.title}
          onChange={(e) => setNewFeed({ ...newFeed, title: e.target.value })}
        />
        <input
          type="text"
          placeholder="Feed URL"
          value={newFeed.url}
          onChange={(e) => setNewFeed({ ...newFeed, url: e.target.value })}
        />
        <input
          type="text"
          placeholder="Category"
          value={newFeed.category}
          onChange={(e) => setNewFeed({ ...newFeed, category: e.target.value })}
        />
        <button type="submit">Add Feed</button>
      </form>

      <h2>Feeds</h2>
      <ul>
        {feeds.map((feed, index) => (
          <li key={index}>
            {feed.title} - {feed.url} ({feed.category})
          </li>
        ))}
      </ul>

      <h2>Entries</h2>
      <ul>
        {entries.map((entry, index) => (
          <li key={index}>
            <a href={entry.url} target="_blank" rel="noopener noreferrer">{entry.title}</a>
            <p>{entry.content}</p>
            <p>Published At: {new Date(entry.published_at).toLocaleString()}</p>
            <p>Hashtags: {entry.hashtags}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

