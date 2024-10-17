import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowUpDown, RefreshCcw, Plus } from 'lucide-react';

const API_BASE_URL = 'http://localhost:4567/api';

const Dashboard = () => {
  const [feeds, setFeeds] = useState([]);
  const [entries, setEntries] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [sortColumn, setSortColumn] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [newFeed, setNewFeed] = useState({ title: '', url: '', category: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const feedsData = await fetch(`${API_BASE_URL}/feeds`).then(res => res.json());
      const entriesData = await fetch(`${API_BASE_URL}/entries`).then(res => res.json());
      const orgsData = await fetch(`${API_BASE_URL}/organizations`).then(res => res.json());
      setFeeds(feedsData);
      setEntries(entriesData);
      setOrganizations(orgsData);
    } catch (error) {
      console.error('Error fetching data:', error);
      // You might want to set an error state here and display it to the user
    }
  };

  const handleSort = (column) => {
    if (column === sortColumn) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const sortedOrganizations = organizations
    .filter(org => org.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      const compare = (a[sortColumn] || '').localeCompare(b[sortColumn] || '');
      return sortDirection === 'asc' ? compare : -compare;
    });

  const feedCounts = feeds.reduce((acc, feed) => {
    acc[feed.category] = (acc[feed.category] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(feedCounts).map(([category, count]) => ({
    category,
    count,
  }));

  const handleSearch = async () => {
    try {
      const results = await fetch(`${API_BASE_URL}/search?q=${searchTerm}`).then(res => res.json());
      setEntries(results);
    } catch (error) {
      console.error('Error searching entries:', error);
      // You might want to set an error state here and display it to the user
    }
  };

  const handleAddFeed = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/feeds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newFeed),
      });
      if (response.ok) {
        fetchData();
        setNewFeed({ title: '', url: '', category: '' });
      } else {
        throw new Error('Failed to add feed');
      }
    } catch (error) {
      console.error('Error adding feed:', error);
      // You might want to set an error state here and display it to the user
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">PR Monitoring Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Feed Distribution</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Entries</h2>
          <ul className="list-disc pl-5">
            {entries.slice(0, 5).map((entry, index) => (
              <li key={index} className="mb-2">
                <a href={entry.url} target="_blank" rel="noopener noreferrer" className="font-semibold">{entry.title}</a>
                <p className="text-sm text-gray-600">Hashtags: {entry.hashtags}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Add New Feed</h2>
        <div className="flex space-x-4">
          <input
            className="flex-1 px-3 py-2 border rounded"
            placeholder="Title"
            value={newFeed.title}
            onChange={(e) => setNewFeed({...newFeed, title: e.target.value})}
          />
          <input
            className="flex-1 px-3 py-2 border rounded"
            placeholder="URL"
            value={newFeed.url}
            onChange={(e) => setNewFeed({...newFeed, url: e.target.value})}
          />
          <input
            className="flex-1 px-3 py-2 border rounded"
            placeholder="Category"
            value={newFeed.category}
            onChange={(e) => setNewFeed({...newFeed, category: e.target.value})}
          />
          <button onClick={handleAddFeed} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center">
            <Plus className="mr-2 h-4 w-4" /> Add Feed
          </button>
        </div>
      </div>
      
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Organizations</h2>
        <div className="mb-4 flex justify-between items-center">
          <input
            className="px-3 py-2 border rounded mr-2"
            placeholder="Search entries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button onClick={handleSearch} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mr-2">Search</button>
          <button onClick={fetchData} className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center">
            <RefreshCcw className="mr-2 h-4 w-4" /> Refresh
          </button>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('name')}>
                Name <ArrowUpDown className="inline-block h-4 w-4" />
              </th>
              <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('website')}>
                Website <ArrowUpDown className="inline-block h-4 w-4" />
              </th>
              <th className="p-2 text-left cursor-pointer" onClick={() => handleSort('category')}>
                Category <ArrowUpDown className="inline-block h-4 w-4" />
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedOrganizations.map((org, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                <td className="p-2">{org.name}</td>
                <td className="p-2"><a href={org.website} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">{org.website}</a></td>
                <td className="p-2">{org.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
