from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# API keys
GOOGLE_PLACES_API_KEY = 'AIzaSyAnF6iacl7OEzOwJ8N95Njqoo0HeBASWZ4'
TMDB_API_KEY = '7673312aa2872a431795a2ae7752a85d'

# In-memory storage for votes and shared restaurant data
votes = {
    'restaurants': {},
    'events': {},
    'movies': {}
}
shared_restaurants = []  # Shared storage for restaurant data

# Route to serve the Intro Page
@app.route("/")
def intro():
    return render_template("intro.html")

# Route to serve the Voting Page
@app.route("/index")
def index():
    return render_template("index.html")

# Function to get nearby restaurants
def get_restaurants(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 2000,
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get('results', [])

# Function to get nearby events
def get_events(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "type": "establishment",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get('results', [])

# Function to get current movies from TMDb
def get_current_movies():
    url = f"https://api.themoviedb.org/3/movie/now_playing"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(url, params=params)
    return response.json().get('results', [])

# Endpoint to fetch restaurants and broadcast to all clients
@app.route('/fetch_restaurants', methods=['POST'])
def fetch_restaurants():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    
    # Fetch restaurants based on location
    global shared_restaurants
    shared_restaurants = get_restaurants(latitude, longitude)
    
    # Broadcast restaurant data to all connected clients
    socketio.emit('restaurant_update', {'restaurants': shared_restaurants})
    
    return jsonify(shared_restaurants)

# Endpoint to fetch events
@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    events = get_events(latitude, longitude)
    return jsonify(events)

# Endpoint to fetch movies
@app.route('/fetch_movies', methods=['GET'])
def fetch_movies():
    movies = get_current_movies()
    return jsonify(movies)

# Endpoint to handle voting
@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    data = request.json
    item_name = data['item']
    vote = data['vote']
    item_type = data['type']

    # Initialize vote count if item doesn't exist yet
    if item_name not in votes[item_type]:
        votes[item_type][item_name] = 0

    # Adjust vote count based on Yes or No vote
    if vote == 'yes':
        votes[item_type][item_name] += 1
    elif vote == 'no':
        votes[item_type][item_name] -= 1

    # Find the current leader
    leader_name, leader_votes = max(votes[item_type].items(), key=lambda x: x[1], default=(None, 0))
    leader = {'name': leader_name, 'votes': leader_votes}

    # Emit real-time leaderboard update to all clients
    socketio.emit('vote_update', {'type': item_type, 'leader': leader})

    return jsonify({'status': 'success', 'leader': leader})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
