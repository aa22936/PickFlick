from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# In-memory storage for groups and votes
groups = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    group_id = request.args.get('group_id', type=int)  # Get group_id from the URL
    group_info = groups.get(group_id) if group_id else None  # Get group data if group_id exists

    if request.method == 'POST':
        if 'create_group' in request.form:
            # Handle creating a group
            group_name = request.form['group_name']
            group_id = len(groups) + 1  # Simple group ID assignment
            groups[group_id] = {
                "name": group_name,
                "restaurants": [],
                "votes": {}
            }
            return redirect(url_for('home', group_id=group_id))

        elif 'add_restaurants' in request.form:
            # Handle adding restaurants to a group
            group_id = request.form['group_id']
            if group_id:
                group_id = int(group_id)
                restaurants = request.form['restaurants'].split(',')
                groups[group_id]["restaurants"] = restaurants
                groups[group_id]["votes"] = {restaurant: [] for restaurant in restaurants}
                return redirect(url_for('home', group_id=group_id))

        elif 'vote' in request.form:
            # Handle voting for a restaurant (like/dislike)
            group_id = request.form['group_id']
            restaurant = request.form['restaurant']
            user_id = request.form['user_id']
            vote = request.form['vote'] == 'yes'  # Convert 'yes' to True, 'no' to False

            # Record the vote
            groups[int(group_id)]["votes"][restaurant].append({"user_id": user_id, "vote": vote})
            return redirect(url_for('home', group_id=group_id))

    return render_template('index.html', groups=groups, group_info=group_info, group_id=group_id)

@app.route('/results/<int:group_id>', methods=['GET'])
def results(group_id):
    if group_id not in groups:
        return jsonify({"error": "Group not found"}), 404

    group_votes = groups[group_id]["votes"]
    results = {}
    for restaurant, restaurant_votes in group_votes.items():
        positive_votes = sum(v["vote"] for v in restaurant_votes)
        if positive_votes >= len(restaurant_votes) / 2:  # Majority rule
            results[restaurant] = "Selected"
        else:
            results[restaurant] = f"{positive_votes}/{len(restaurant_votes)} positive votes"
    
    # Pass both groups and results to the template
    return render_template('results.html', groups=groups, results=results, group_id=group_id)


if __name__ == '__main__':
    app.run(debug=True)
