# webhook-repo

Flask application to receive GitHub webhook events and store them in MongoDB.

## Features

- Accepts GitHub webhook events: `push`, `pull_request`, `merge`
- Stores data in MongoDB
- Minimal UI that polls every 15 seconds
- Displays events in clean readable format

## MongoDB Schema

```json
{
  "author": "Travis",
  "event_type": "push",
  "from_branch": null,
  "to_branch": "staging",
  "timestamp": "2021-04-01T21:30:00Z"
}
