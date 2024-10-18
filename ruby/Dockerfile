# Use an official Ruby runtime as a parent image
FROM ruby:3.2

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Copy the Gemfile and Gemfile.lock
COPY . .
# Install Ruby dependencies
RUN bundle install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 4567

# Start Redis server, Sidekiq, and the Sinatra app
CMD redis-server --daemonize yes && bundle exec sidekiq -r ./app.rb & bundle exec ruby app.rb -o 0.0.0.0
