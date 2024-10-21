# PRSS: Fuss Monitor
Aggregate RSS feeds and extract press releases from your competitors in order to automatically analyze them with AI to generate competitive marketing/PR strategies for startups and influencers.

![Screenshot](/screenshot.jpg?raw=true "Preview")

This application is a full-stack solution for monitoring Press Release RSS feeds. It includes a Sinatra backend API, Sidekiq workers for background processing, and a React frontend.

## Development

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
pip install -r requirements.txt
This command will install all the listed packages and their dependencies.
If you're using a virtual environment (which is recommended), make sure to activate it before installing the requirements.

Note: The versions specified in the requirements.txt file are the latest stable versions as of my knowledge cutoff. You may want to update these to the latest versions available when you're setting up your project, or remove the version specifications entirely to always get the latest versions (though this can sometimes lead to compatibility issues).


python-dotenv allows you to use a .env file to manage environment variables, which can be useful for managing configuration across different environments (development, staging, production).

Remember, if you add any new Python packages to your project in the future, make sure to update the requirements.txt file. You can do this manually, or by running:

pip freeze > requirements.txt
This command will update the requirements.txt file with all currently installed packages in your environment.
