# PRSS
Extract press releases from your competitors and analyze them with AI to generate more competitive marketing and PR strategies.


# PR Monitoring Dashboard

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
