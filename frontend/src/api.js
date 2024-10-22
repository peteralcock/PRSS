import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

// Get all feeds
export const getFeeds = async () => {
  const response = await axios.get(`${API_BASE_URL}/feeds`);
  return response.data;
};

// Add a new feed
export const addFeed = async (feed) => {
  const response = await axios.post(`${API_BASE_URL}/feeds`, feed);
  return response.data;
};

// Get all entries
export const getEntries = async () => {
  const response = await axios.get(`${API_BASE_URL}/entries`);
  return response.data;
};

