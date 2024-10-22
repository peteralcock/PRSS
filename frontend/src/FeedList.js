import React, { useState, useEffect } from 'react';
import { getFeeds } from './api';

const FeedList = () => {
  const [feeds, setFeeds] = useState([]);

  useEffect(() => {
    const fetchFeeds = async () => {
      const feeds = await getFeeds();
      setFeeds(feeds);
    };
    fetchFeeds();
  }, []);

  return (
    <div>
      <h2>Feeds</h2>
      <ul>
        {feeds.map((feed, index) => (
          <li key={index}>
            <strong>{feed.title}</strong> - <a href={feed.url} target="_blank" rel="noreferrer">{feed.url}</a> - {feed.category}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FeedList;

