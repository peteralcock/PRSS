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
