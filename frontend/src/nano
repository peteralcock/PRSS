import React, { useState } from 'react';
import { addFeed } from './api';

const AddFeed = ({ onAdd }) => {
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [category, setCategory] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newFeed = { title, url, category };
    await addFeed(newFeed);
    onAdd(); // To refresh the feed list
    setTitle('');
    setUrl('');
    setCategory('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Add New Feed</h2>
      <div>
        <label>Title:</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div>
        <label>URL:</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Category:</label>
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        />
      </div>
      <button type="submit">Add Feed</button>
    </form>
  );
};

export default AddFeed;

