from dataclasses import dataclass

import flask
import functions_framework
import requests


@dataclass
class GitHubLabel:
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: str


@functions_framework.http
def forwarder(request: flask.Request):
    """
    
    """

    event = request.headers.get("X-GitHub-Event")
    print(f"{event = }")
    if event == "pull_request":
        labels = [
            GitHubLabel(**label)
            for label in request.json["pull_request"]["labels"]
        ]
        if not labels:
            return "No labels", 400

        forward_to = [
            l.name.split("fwd:")[-1]
            for l in labels
            if l.name.startswith("fwd:")
        ]
        if not forward_to:
            return "No labels starting with 'fwd:'", 400

    for recipient in forward_to:
        print(f"Forwarding GitHub webhook to {recipient = }")
        requests.post(
            f"https://{recipient}",
            headers=request.headers,
            json=request.json,
        )
    return f"Forwarded to {forward_to}", 200
