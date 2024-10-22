import React, { useState } from 'react';
import FeedList from './FeedList';
import AddFeed from './AddFeed';
import EntryList from './EntryList';

const App = () => {
  const [feedsUpdated, setFeedsUpdated] = useState(false);

  const handleFeedAdded = () => {
    setFeedsUpdated(!feedsUpdated); // Toggle to refresh feeds
  };

  return (
    <div>
      <h1>PRSS - PR Monitoring</h1>
      <AddFeed onAdd={handleFeedAdded} />
      <FeedList key={feedsUpdated} />
      <EntryList />
    </div>
  );
};

export default App;

