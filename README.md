# PRSS: Press Release Monitor
Aggregate RSS feeds and extract press releases from your competitors in order to automatically analyze them with AI to generate competitive marketing/PR strategies for startups and influencers.

![Screenshot](/screenshot.jpg?raw=true "Preview")

This application is a full-stack solution for monitoring PR feeds. It includes a Sinatra backend API, Sidekiq workers for background processing, and a React frontend.

### Setup

1. Install dependencies:
   ```
   bundle install
   ```

2. Set up the database:
   The application uses SQLite. The database will be created automatically when you run the app.

3. Start the Sinatra server:
   ```
   ruby app.rb
   ```

4. Start Sidekiq (in a separate terminal):
   ```
   bundle exec sidekiq -r ./app.rb
   ```

5. Open a web browser and navigate to `http://localhost:4567`




### Front-End

Current Setup (Simple, In-Browser React):

1. The React code is embedded directly in the `public/index.html` file.
2. React and other dependencies are loaded via CDN links in the HTML file.
3. Babel is used for in-browser transpilation of JSX.

To use this setup:

1. Ensure the `public/index.html` file is in your project's `public` folder.
2. Make sure your Sinatra app is configured to serve static files from the `public` folder:

```ruby
set :public_folder, File.dirname(__FILE__) + '/public'
```

3. When you run your Sinatra app (`ruby app.rb`), it will serve the React frontend at the root URL (`http://localhost:4567`).

This setup doesn't require any additional build steps for the frontend, but it's not optimal for larger applications or production use.

For a more robust setup using Create React App:

1. Create a new React app in a separate directory:

```bash
npx create-react-app pr-monitoring-frontend
cd pr-monitoring-frontend
```

2. Replace the contents of `src/App.js` with our Dashboard component. You'll need to make some modifications:

   - Import React and hooks at the top:
     ```javascript
     import React, { useState, useEffect } from 'react';
     ```
   - Import Recharts components:
     ```javascript
     import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
     ```
   - Install and import icons:
     ```bash
     npm install lucide-react
     ```
     Then in your React component:
     ```javascript
     import { Plus, RefreshCcw, ArrowUpDown } from 'lucide-react';
     ```

3. Install additional dependencies:

```bash
npm install recharts
```

4. Update the `API_BASE_URL` in your React component to point to your Sinatra backend:

```javascript
const API_BASE_URL = 'http://localhost:4567/api';
```

5. In the React app's `package.json`, add a proxy to avoid CORS issues during development:

```json
{
  ...
  "proxy": "http://localhost:4567"
}
```

6. Start your React development server:

```bash
npm start
```

Your React app will now be available at `http://localhost:3000` and will proxy API requests to your Sinatra backend at `http://localhost:4567`.

7. For production, build your React app:

```bash
npm run build
```

8. Copy the contents of the `build` folder to your Sinatra app's `public` folder.

9. Update your Sinatra app to serve the React app:

```ruby
get '/*' do
  send_file File.join(settings.public_folder, 'index.html')
end
```

This catch-all route should be the last route in your Sinatra app to allow your API routes to work correctly.

With this setup, you'll have a more maintainable and production-ready frontend, with proper build processes and optimizations.

Remember to handle CORS properly in your Sinatra backend if you're running the frontend and backend on different domains or ports in production.

This setup gives you the flexibility to develop your frontend independently while still integrating seamlessly with your Sinatra backend.



## Python Development

Here's an explanation of each package:

Flask: The core web framework we're using.
Flask-SQLAlchemy: An extension for Flask that adds support for SQLAlchemy, our ORM.
Flask-CORS: An extension for handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
celery: For handling background tasks and scheduled jobs.
feedparser: A library for parsing RSS and Atom feeds.
redis: Used as a message broker for Celery.
gunicorn: A production-ready WSGI server for deploying Flask applications.

To use this requirements.txt file:

Save it in the same directory as your app.py file.
Install all the requirements using pip:
Copypip install -r requirements.txt
This command will install all the listed packages and their dependencies.
If you're using a virtual environment (which is recommended), make sure to activate it before installing the requirements.

Note: The versions specified in the requirements.txt file are the latest stable versions as of my knowledge cutoff. You may want to update these to the latest versions available when you're setting up your project, or remove the version specifications entirely to always get the latest versions (though this can sometimes lead to compatibility issues).
For development purposes, you might also want to add:
Copypython-dotenv==1.0.0
This package allows you to use a .env file to manage environment variables, which can be useful for managing configuration across different environments (development, staging, production).
Remember, if you add any new Python packages to your project in the future, make sure to update the requirements.txt file. You can do this manually, or by running:
Copypip freeze > requirements.txt
This command will update the requirements.txt file with all currently installed packages in your environment.




## NodeJS Development

To set up and run this Node.js version of the PR Monitoring application:

1. Make sure you have Node.js and npm installed on your system.

2. Create a new directory for your project and navigate into it:

   ```
   mkdir pr-monitoring-nodejs && cd pr-monitoring-nodejs
   ```

3. Create the `app.js` and `package.json` files with the content provided above.

4. Install the dependencies:

   ```
   npm install
   ```

5. Create a `public` folder in the same directory as `app.js` and place your React frontend files there (index.html and any other static assets).

6. Start the application:

   ```
   npm start
   ```

   Or for development with auto-restart on file changes:

   ```
   npm run dev
   ```

This Node.js version provides similar functionality to the Ruby/Sinatra version:

- It uses Sequelize for database operations (equivalent to Sequel in the Ruby version).
- Bull is used for background tasks (equivalent to Sidekiq).
- The API endpoints (`/api/feeds`, `/api/entries`, `/api/search`) function the same way as in the Sinatra version.
- It serves the React frontend from the `public` folder.
- The feed fetching is scheduled to run every hour using `setInterval`.

Main differences and considerations:

1. Database: It uses SQLite by default. For production, you might want to switch to PostgreSQL or MySQL.

2. ORM: Sequelize is used instead of Sequel. The models (Feed and Entry) are defined using Sequelize's `define` method.

3. Background Jobs: Bull is used for background job processing. The feed processing logic is defined in the `feedQueue.process` function.

4. CORS: The `cors` middleware is used to handle Cross-Origin Resource Sharing.

5. Feed Parsing: We're using the `feedparser` package to parse RSS feeds.

6. Scheduling: A simple `setInterval` is used for scheduling. For more complex scheduling needs, you might want to use a package like `node-cron`.

Remember to adjust the React frontend to point to these new Node.js endpoints (they should be the same as before, just served by Express instead of Sinatra).

This Node.js version should be a drop-in replacement for the Sinatra version, providing the same functionality with a JavaScript backend.
