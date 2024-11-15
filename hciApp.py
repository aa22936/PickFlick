from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
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
leader_client_id = 'leader_id'  # Replace with an actual identifier for the leader

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
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching restaurants: {e}")
        return {"error": "Failed to fetch restaurants"}

# Function to get events
def get_events(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "type": "point_of_interest",
        "keyword": "event venue",
        "key": GOOGLE_PLACES_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return {"error": "Failed to fetch events"}

# Function to get current movies from TMDb
def get_current_movies():
    url = "https://api.themoviedb.org/3/movie/now_playing"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print("TMDb API Response:", data)
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies: {e}")
        return {"error": "Failed to fetch movies"}

# Endpoint to fetch restaurants
@app.route('/fetch_restaurants', methods=['POST'])
def fetch_restaurants():
    client_id = request.json.get('client_id')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')

    global shared_restaurants
    shared_restaurants = get_restaurants(latitude, longitude)

    # Populate votes dictionary
    for restaurant in shared_restaurants:
        votes['restaurants'][restaurant['name']] = 0

    if client_id == leader_client_id:
        socketio.emit('restaurant_update', {'restaurants': shared_restaurants})

    return jsonify(shared_restaurants)


# Endpoint to fetch events
@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    events = get_events(latitude, longitude)

    # Populate the votes dictionary
    for event in events:
        if event['name'] not in votes['events']:
            votes['events'][event['name']] = 0

    print(f"Populated events in votes: {votes['events']}")  # Debugging
    return jsonify(events)



# Endpoint to fetch movies
@app.route('/fetch_movies', methods=['GET'])
def fetch_movies():
    movies = get_current_movies()

    # Populate votes dictionary with normalized keys
    for movie in movies:
        normalized_name = movie['title'].strip().lower()
        if normalized_name not in votes['movies']:
            votes['movies'][normalized_name] = 0

    print(f"Populated movies in votes: {votes['movies']}")  # Debugging
    return jsonify(movies)


# Endpoint to handle item deletion
@app.route('/delete_item', methods=['POST'])
def delete_item():
    data = request.json
    item_name = data['item'].strip().lower()  # Normalize input
    item_type = data['type']

    print(f"Attempting to delete normalized item: {item_name} of type: {item_type}")  # Debugging
    normalized_votes = {k.strip().lower(): k for k in votes.get(item_type, {})}  # Normalize stored keys

    if item_name in normalized_votes:
        original_name = normalized_votes[item_name]  # Find the original key
        del votes[item_type][original_name]
        print(f"Deleted item: {original_name} from type: {item_type}")  # Debugging
        return jsonify({'status': 'success'})
    else:
        print(f"Item {item_name} not found in type: {item_type}")  # Debugging
        return jsonify({'status': 'error', 'error': 'Item not found'})




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
