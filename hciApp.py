from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for groups and votes
groups = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'create_group' in request.form:
            # Handle creating a group
            group_name = request.form['group_name']
            group_id = len(groups) + 1
            groups[group_id] = {
                "name": group_name,
                "items": [],
                "votes": {}
            }
            return redirect(url_for('home', group_id=group_id))

        elif 'add_items' in request.form:
            # Handle adding items to a group
            group_id = request.form['group_id']
            if group_id:
                group_id = int(group_id)
                items = request.form['items'].split(',')
                groups[group_id]["items"] = items
                groups[group_id]["votes"] = {item: [] for item in items}
                return redirect(url_for('home', group_id=group_id))

        elif 'vote' in request.form:
            # Handle voting for an item
            group_id = request.form['group_id']
            item = request.form['item']
            user_id = request.form['user_id']
            vote = request.form['vote'] == 'yes'  # Convert 'yes' to True, 'no' to False

            # Record the vote
            groups[int(group_id)]["votes"][item].append({"user_id": user_id, "vote": vote})
            return redirect(url_for('home', group_id=group_id))

    # Render the page with current group data
    group_id = request.args.get('group_id', type=int)
    group_info = groups.get(group_id) if group_id else None

    return render_template('index.html', groups=groups, group_info=group_info)

@app.route('/results/<int:group_id>', methods=['GET'])
def results(group_id):
    if group_id not in groups:
        return jsonify({"error": "Group not found"}), 404

    group_votes = groups[group_id]["votes"]
    results = {}
    for item, item_votes in group_votes.items():
        positive_votes = sum(v["vote"] for v in item_votes)
        if positive_votes >= len(item_votes) / 2:  # Majority rule
            results[item] = "Selected"
        else:
            results[item] = f"{positive_votes}/{len(item_votes)} positive votes"
    
    return render_template('results.html', results=results, group_id=group_id)

if __name__ == '__main__':
    app.run(debug=True)
