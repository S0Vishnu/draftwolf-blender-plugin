"""API client for DraftWolf local server."""

import json
import urllib.request
import urllib.error

from .constants import API_URL


def send_request(endpoint, data=None):
    url = f"{API_URL}{endpoint}"
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'DraftWolf-Blender/1.0')

    if data:
        jsondata = json.dumps(data).encode('utf-8')
        req.data = jsondata  # IMPLIES POST

    try:
        with urllib.request.urlopen(req, timeout=2.0) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"DraftWolf API Error: {e.code}")
        try:
            err_body = e.read().decode('utf-8')
            return json.loads(err_body)
        except Exception:
            return {'success': False, 'error': f"HTTP {e.code}"}
    except OSError as e:
        print(f"DraftWolf Connection Error: {e}")
        return {'success': False, 'error': str(e)}
