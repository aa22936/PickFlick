from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

# In-memory storage for groups and votes
groups = {}

# Google Places API key
GOOGLE_PLACES_API_KEY = 'AIzaSyAnF6iacl7OEzOwJ8N95Njqoo0HeBASWZ4'

# TMDb API key
TMDB_API_KEY = '7673312aa2872a431795a2ae7752a85d'

# Function to get nearby restaurants
def get_restaurants(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 2000,  # Search within 2000 meters
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get('results', [])

# Function to get nearby events (like bowling, bars, etc.)
def get_events(latitude, longitude):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,  # Search within 5000 meters
        "type": "establishment",  # Can be changed to more specific types like "bar", "bowling_alley"
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
    data = response.json()
    return data.get('results', [])

@app.route('/', methods=['GET', 'POST'])
def home():
    group_id = request.args.get('group_id', type=int)
    group_info = groups.get(group_id) if group_id else None

    if request.method == 'POST':
        if 'create_group' in request.form:
            group_name = request.form['group_name']
            group_id = len(groups) + 1
            groups[group_id] = {
                "name": group_name,
                "restaurants": [],
                "votes": {}
            }
            return redirect(url_for('home', group_id=group_id))

        elif 'add_restaurants' in request.form:
            group_id = request.form['group_id']
            if group_id:
                group_id = int(group_id)
                restaurants = request.form['restaurants'].split(',')
                groups[group_id]["restaurants"] = restaurants
                groups[group_id]["votes"] = {restaurant: [] for restaurant in restaurants}
                return redirect(url_for('home', group_id=group_id))

        elif 'vote' in request.form:
            group_id = request.form['group_id']
            restaurant = request.form['restaurant']
            user_id = request.form['user_id']
            vote = request.form['vote'] == 'yes'
            groups[int(group_id)]["votes"][restaurant].append({"user_id": user_id, "vote": vote})
            return redirect(url_for('home', group_id=group_id))

    return render_template('index.html', groups=groups, group_info=group_info, group_id=group_id)

@app.route('/fetch_restaurants', methods=['POST'])
def fetch_restaurants():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    restaurants = get_restaurants(latitude, longitude)
    return jsonify(restaurants)

@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    events = get_events(latitude, longitude)
    return jsonify(events)

@app.route('/fetch_movies', methods=['GET'])
def fetch_movies():
    movies = get_current_movies()
    return jsonify(movies)

@app.route('/results/<int:group_id>', methods=['GET'])
def results(group_id):
    if group_id not in groups:
        return jsonify({"error": "Group not found"}), 404

    group_votes = groups[group_id]["votes"]
    results = {}
    for restaurant, restaurant_votes in group_votes.items():
        positive_votes = sum(v["vote"] for v in restaurant_votes)
        if positive_votes >= len(restaurant_votes) / 2:
            results[restaurant] = "Selected"
        else:
            results[restaurant] = f"{positive_votes}/{len(restaurant_votes)} positive votes"

    return render_template('results.html', groups=groups, results=results, group_id=group_id)


if __name__ == '__main__':
    app.run(debug=True)
