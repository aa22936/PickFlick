from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

# API keys extracted from your file
GOOGLE_PLACES_API_KEY = "AIzaSyAnF6iacl7OEzOwJ8N95Njqoo0HeBASWZ4"
TMDB_API_KEY = "7673312aa2872a431795a2ae7752a85d"

# Routes to serve the HTML files
@app.route('/')
def serve_intro():
    return render_template('intro.html')  # Serve intro.html from templates

@app.route('/index')
def serve_voting_page():
    return render_template('index.html')  # Serve index.html from templates

@app.route('/results')
def serve_results():
    return render_template('results.html')  # Serve results.html from templates

# API to fetch nearby restaurants using Google Places API
@app.route('/fetch_restaurants', methods=['POST'])
def fetch_restaurants():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": 1500,
        "type": "restaurant",
        "key": GOOGLE_PLACES_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        places = response.json().get('results', [])
        restaurants = [{"name": place['name'], "vicinity": place.get('vicinity', 'Address not available')} for place in places]
        return jsonify(restaurants)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching restaurants: {e}")
        return jsonify({"error": "Failed to fetch restaurants"}), 500

# API to fetch nearby events using Google Places API
@app.route('/fetch_events', methods=['POST'])
def fetch_events():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
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
        places = response.json().get('results', [])
        events = [{"name": place['name'], "address": place.get('vicinity', 'Address not available')} for place in places]
        return jsonify(events)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return jsonify({"error": "Failed to fetch events"}), 500

# API to fetch movies using TMDB API
@app.route('/fetch_movies', methods=['GET'])
def fetch_movies():
    url = f"https://api.themoviedb.org/3/movie/now_playing"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        movies = response.json().get('results', [])
        formatted_movies = [
            {"title": movie['title'], "overview": movie.get('overview', 'No description available'), "poster_path": movie.get('poster_path')}
            for movie in movies
        ]
        return jsonify(formatted_movies)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies: {e}")
        return jsonify({"error": "Failed to fetch movies"}), 500

# API to delete items (mock implementation)
@app.route('/delete_item', methods=['POST'])
def delete_item():
    data = request.get_json()
    return jsonify({"status": "success", "item": data['item']})

# API to finalize votes and determine the winner
@app.route('/finalize_votes', methods=['POST'])
def finalize_votes():
    data = request.get_json()
    leader = max(data, key=lambda x: x.get('votes', 0), default=None)
    return jsonify(leader)

if __name__ == '__main__':
    app.run(debug=True)
