# Use an official Node runtime as the parent image
FROM node:16-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json and package-lock.json
COPY package*.json ./

# Install app dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Create a directory for the SQLite database
RUN mkdir -p /usr/src/app/data && \
    touch /usr/src/app/data/pr_monitoring.sqlite && \
    chown -R node:node /usr/src/app/data

# Switch to non-root user
USER node

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["node", "app.js"]
