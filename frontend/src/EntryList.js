import React, { useState, useEffect } from 'react';
import { getEntries } from './api';

const EntryList = () => {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    const fetchEntries = async () => {
      const entries = await getEntries();
      setEntries(entries);
    };
    fetchEntries();
  }, []);

  return (
    <div>
      <h2>Entries</h2>
      <ul>
        {entries.map((entry, index) => (
          <li key={index}>
            <strong>{entry.title}</strong> - <a href={entry.url} target="_blank" rel="noreferrer">{entry.url}</a>
            <p>{entry.content}</p>
            <p><strong>Published At:</strong> {entry.published_at}</p>
            <p><strong>Hashtags:</strong> {entry.hashtags}</p>
            <p><strong>Summary:</strong> {entry.summary}</p>
            <p><strong>Analysis:</strong> {entry.analysis}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EntryList;

