# PickFlick Voting App

PickFlick is a group voting web application that helps groups make decisions on places to eat, events to attend, or movies to watch. Users can search for nearby restaurants, events, and current movies, vote on options, and see which choice is leading.

## Features
- **Intro Page**: Users input the number of people voting.
- **Voting Page**: Users can:
  - Find nearby restaurants and events using location data.
  - Fetch current movies.
  - Manually add options.
  - Cast "Yes" or "No" votes.
  - View the leading option for each category.

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **APIs**:
  - Google Places API for fetching nearby restaurants and events.
  - TMDb API for fetching current movies.

## Prerequisites
1. **Python 3**: Make sure Python is installed on your system.
2. **Flask**: Install Flask by running:
   ```bash
   pip install Flask
