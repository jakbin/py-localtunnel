import json
import requests

LOCAL_TUNNEL_SERVER = "http://localtunnel.me/"

class AssignedUrlInfo:
    def __init__(self, id=None, url=None, port=None, max_conn_count=None):
        self.id = id
        self.url = url
        self.port = port
        self.max_conn_count = max_conn_count

def get_assigned_url(assigned_domain=None):
    if not assigned_domain:
        assigned_domain = "?new"
    url = LOCAL_TUNNEL_SERVER + assigned_domain
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to get assigned URL: {response.text}")
    data = json.loads(response.text)
    if "error" in data:
        raise Exception(f"Failed to get assigned URL: {data['error']}")
    return AssignedUrlInfo(**data)
