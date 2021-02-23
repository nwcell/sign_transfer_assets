import os
import requests
from dotenv import load_dotenv

from .util import BaseUriSession


class Sign:
    def __init__(self, integration_key, base_uri):
        self.integration_key = f"Bearer {integration_key}"

        self.session = BaseUriSession(base_uri)
        self.session.headers.update({"Authorization": self.integration_key})

        self.status = set()

    @property
    def user(self):
        user_string = self.session.headers.get("x-api-user", None)
        if user_string is None:
            return None
        prefix = "email:"
        if user_string.startswith(prefix):
            return user_string[len(prefix) :]

    @user.setter
    def user(self, user):
        self.session.headers.update({"x-api-user": f"email:{user}"})

    @user.deleter
    def user(self):
        self.session.headers.update({"x-api-user": None})

    def validate(self, resp, code=200):
        if resp.status_code != code:
            raise Exception(
                {
                    "issue": "Bad Response",
                    "status_code": resp.status_code,
                    "data": resp.text,
                }
            )

    def base_uri(self):
        pass

    def get_template(self, id):
        url = f"/libraryDocuments/{id}"
        resp = self.session.get(url)
        self.validate(resp)
        return resp.json()

    def get_template_docs(self, id):
        url = f"/libraryDocuments/{id}/documents"
        resp = self.session.get(url)
        self.validate(resp)
        return resp.json()

    def get_template_doc(self, id, doc_id):
        url = f"/libraryDocuments/{id}/documents/{doc_id}"
        resp = self.session.get(url, headers={"Accept": "application/pdf"})
        self.validate(resp)
        return resp.content

    def get_template_doc_files(self, id):
        docs = self.get_template_docs(id)
        for doc in docs["documents"]:
            yield self.get_template_doc(id, doc["id"])

    def get_template_fields(self, id):
        url = f"/libraryDocuments/{id}/formFields"
        resp = self.session.get(url)
        self.validate(resp)
        return resp.json()

    def create_transient(self, doc, mime_type="application/pdf"):
        url = f"/transientDocuments"
        files = {
            "File": doc,
            "Mime-Type": mime_type,
        }
        resp = self.session.post(url, files=files)
        self.validate(resp, code=201)
        return resp.json()

    def bulk_create_transient(self, docs=[]):
        for doc in docs:
            data = self.create_transient(doc)
            yield data["transientDocumentId"]

    def create_template(self, template_data, transient_ids=[]):
        data = {
            "name": template_data["name"],
            "templateTypes": template_data["templateTypes"],
            "sharingMode": "USER",
            "state": "ACTIVE",
            "fileInfos": [{"transientDocumentId": id} for id in transient_ids],
        }
        url = f"/libraryDocuments"
        resp = self.session.post(url, json=data)
        self.validate(resp, code=201)
        return resp.json()

    def update_template_fields(self, id, fields):
        url = f"/libraryDocuments/{id}/formFields"
        resp = self.session.put(url, json=fields)
        self.validate(resp)
        return resp.json()

    def clone_template(self, id, sender=None, reciever=None):
        old_user = self.user
        if sender:
            self.user = sender

        # Fetch Template Data
        template_data = self.get_template(id)
        docs = self.get_template_doc_files(id)
        fields = self.get_template_fields(id)

        if reciever:
            self.user = reciever

        # Create new Template
        # print([doc for doc in docs])
        transient_ids = self.bulk_create_transient(docs)
        new_template = self.create_template(template_data, transient_ids)
        self.update_template_fields(new_template["id"], fields)

        self.user = old_user

        return new_template["id"]


if __name__ == "__main__":
    load_dotenv()
    integration_key = os.getenv("INTEGRATION_KEY")
    base_uri = os.getenv("BASE_URI") + "api/rest/v6/"
    sign = Sign(integration_key, base_uri)

    template = "CBJCHBCAABAApwrYpRhhMqui0AVAW1WPkE6mcNWaBdfs"
    sender = "travis@houseofkrause.org"
    reciever = "travis@houseofkrause.org"

    out = sign.clone_template(template, sender, reciever)

    print(out)
