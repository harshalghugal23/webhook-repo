# webhook-repo/app.py

from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# === MongoDB Config ===
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['webhook_db']
collection = db['events']

@app.route('/')
def index():
    events = list(collection.find().sort("timestamp", -1))
    return render_template('index.html', events=events)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    event = request.headers.get('X-GitHub-Event', 'unknown')

    if event == 'push':
        author = payload['pusher']['name']
        to_branch = payload['ref'].split('/')[-1]
        timestamp = datetime.utcnow()

        data = {
            "author": author,
            "event_type": "push",
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        collection.insert_one(data)

    elif event == 'pull_request':
        action = payload['action']
        if action == 'opened':
            author = payload['pull_request']['user']['login']
            from_branch = payload['pull_request']['head']['ref']
            to_branch = payload['pull_request']['base']['ref']
            timestamp = datetime.strptime(payload['pull_request']['created_at'], "%Y-%m-%dT%H:%M:%SZ")

            data = {
                "author": author,
                "event_type": "pull_request",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            }
            collection.insert_one(data)

    elif event == 'pull_request' and payload['action'] == 'closed' and payload['pull_request']['merged']:
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.strptime(payload['pull_request']['merged_at'], "%Y-%m-%dT%H:%M:%SZ")

        data = {
            "author": author,
            "event_type": "merge",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        collection.insert_one(data)

    return jsonify({"message": "Event received"}), 200

@app.route('/events')
def get_events():
    events = list(collection.find().sort("timestamp", -1))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
