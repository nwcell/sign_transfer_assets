from requests import Session
from urllib.parse import urljoin


class BaseUriSession(Session):
    def __init__(self, base_uri=""):
        self.base_uri = base_uri.rstrip("/") + "/"

        super(BaseUriSession, self).__init__()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_uri, url.lstrip("/"))
        return super(BaseUriSession, self).request(method, url, *args, **kwargs)
