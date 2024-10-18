


require 'sinatra'
require 'sinatra/json'
require 'sinatra/cors'
require 'sequel'
require 'sidekiq'
require 'sidekiq/web'
require 'feedjira'

# Database setup
DB = Sequel.connect('sqlite://pr_monitoring.db')

DB.create_table? :feeds do
  primary_key :id
  String :title
  String :url
  String :category
end

DB.create_table? :entries do
  primary_key :id
  foreign_key :feed_id, :feeds
  String :title
  String :url
  String :content
  DateTime :published_at
  String :hashtags
end

# Models
class Feed < Sequel::Model; end
class Entry < Sequel::Model; end

# CORS configuration
set :allow_origin, "http://localhost:3000"
set :allow_methods, "GET,HEAD,POST"
set :allow_headers, "content-type,if-modified-since"
set :expose_headers, "location,link"

# Sidekiq Web UI
use Rack::Session::Cookie, secret: "some_secret", same_site: true, max_age: 86400
run Sidekiq::Web

# Workers
class FeedFetcherWorker
  include Sidekiq::Worker

  def perform(feed_id)
    feed = Feed[feed_id]
    response = HTTParty.get(feed.url)
    
    if response.success?
      parsed_feed = Feedjira.parse(response.body)
      process_feed_entries(feed, parsed_feed.entries)
    else
      logger.error "Failed to fetch feed: #{feed.url}"
    end
  end

  private

  def process_feed_entries(feed, entries)
    entries.each do |entry|
      existing_entry = Entry.find(url: entry.url)
      
      if existing_entry
        update_entry(existing_entry, entry)
      else
        create_entry(feed, entry)
      end
    end
  end

  def update_entry(existing_entry, new_entry)
    existing_entry.update(
      title: new_entry.title,
      content: new_entry.content || new_entry.summary,
      published_at: new_entry.published
    )
  end

  def create_entry(feed, entry)
    Entry.create(
      feed: feed,
      title: entry.title,
      url: entry.url,
      content: entry.content || entry.summary,
      published_at: entry.published,
      hashtags: generate_hashtags(entry.title, entry.content || entry.summary)
    )
  end

  def generate_hashtags(title, content)
    combined_text = "#{title} #{content}"
    words = combined_text.downcase.scan(/\w+/)
    words.uniq.select { |word| word.length > 5 }.map { |word| "##{word}" }.join(' ')
  end
end

class FeedSchedulerWorker
  include Sidekiq::Worker

  def perform
    Feed.each do |feed|
      FeedFetcherWorker.perform_async(feed.id)
    end
  end
end

# API routes
get '/api/feeds' do
  json Feed.all
end

get '/api/entries' do
  json Entry.order(Sequel.desc(:published_at)).limit(20)
end

get '/api/search' do
  query = params[:q]
  json Entry.where(Sequel.like(:title, "%#{query}%")).or(Sequel.like(:content, "%#{query}%"))
end

post '/api/feeds' do
  data = JSON.parse(request.body.read)
  feed = Feed.create(data)
  FeedFetcherWorker.perform_async(feed.id)
  json success: true, id: feed.id
end

# Serve the React app
get '/' do
  send_file File.join(settings.public_folder, 'index.html')
end

