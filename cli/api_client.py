"""HTTP client for the copycat server API."""

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from config import Config


@dataclass
class APIResponse:
    status: int
    body: bytes

class APIClient:
    """HTTP client for the copycat server API."""
    def __init__(self, config: Config):
        self.config = config
        self.auth_header = self._basic_auth()


    def _basic_auth(self) -> str:
        token = base64.b64encode(f"{self.config.user_id}:{self.config.api_key}".encode()).decode()
        return f"Basic {token}"

    def _request(self, path: str, method: str = "GET", params=None, data: bytes = None) -> APIResponse:
        url = f"{self.config.server_url}/{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Authorization": self.auth_header},
            method=method,
        )

        try:
            with urllib.request.urlopen(req) as resp:
                return APIResponse(status=resp.status, body=resp.read())
        except urllib.error.HTTPError as e:
            return APIResponse(status=e.code, body=e.read())
        except urllib.error.URLError as e:
            raise ConnectionError(f"Request to {url} failed: {e.reason}") from e

    def post_clipboard(self, text: str | None = None, html: str | None= None, file_path: str | None= None):
        path = f"/clipboard"
        headers = {"Authorization": self.auth_header}
        if not file_path:
            headers["Content-Type"] = "application/json"
            body = dict()
            if not text:
                body["text"] = text
            if not html:
                body["html"] = html
            data = json.dumps(body).encode()
            response = self._request(path, method="POST", data=data)
        else:
            headers["Content-Type"] = "multipart/form-data"



def post_clipboard(config: Config, text: str = "", html: str = "", file_path: str = ""):
    """
    POST /clipboard — send content to the server.
    """
    url = f"{config.server_url}/clipboard"
    headers = {"Authorization": _auth_header(config)}

    if file_path:
        # TODO: multipart/form-data upload
        raise NotImplementedError("File upload not yet implemented")
    else:
        headers["Content-Type"] = "application/json"
        body = dict()
        if not text:
            body["text"] = text
        if not html:
            body["html"] = html

        data = json.dumps(body).encode()


    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_clipboard(config: Config) -> dict:
    """GET /clipboard — retrieve content from the server."""
    url = f"{config.server_url}/clipboard"
    headers = {"Authorization": _auth_header(config)}

    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
