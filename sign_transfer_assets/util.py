from requests import Session
from urllib.parse import urljoin


class SignSession(Session):
    def __init__(self, base_uri="", integration_key=None, user=None):
        super(SignSession, self).__init__()

        self.base_uri = base_uri.rstrip("/") + "/"
        self.integration_key = integration_key
        self.user = user

    @property
    def integration_key(self):
        user_string = self.headers.get("Authorization", None)
        if user_string is None:
            return None
        prefix = "Bearer "
        if user_string.startswith(prefix):
            return user_string[len(prefix) :]

    @integration_key.setter
    def integration_key(self, integration_key):
        self.headers.update({"Authorization": f"Bearer {integration_key}"})

    @integration_key.deleter
    def integration_key(self):
        self.headers.update({"Authorization": None})

    @property
    def user(self):
        user_string = self.headers.get("x-api-user", None)
        if user_string is None:
            return None
        prefix = "email:"
        if user_string.startswith(prefix):
            return user_string[len(prefix) :]

    @user.setter
    def user(self, user):
        self.headers.update({"x-api-user": f"email:{user}"})

    @user.deleter
    def user(self):
        self.headers.update({"x-api-user": None})

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_uri, url.lstrip("/"))
        return super(SignSession, self).request(method, url, *args, **kwargs)
