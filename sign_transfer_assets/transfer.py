import os
from dotenv import load_dotenv

from .util import BaseUriSession
from .main import Sign


class TransferTemplate:
    def __init__(self, sender, reciever):
        self.sender = sender
        self.reciever = reciever

    def clone_template(self, id):
        # Fetch Template Data
        template_data = self.sender.get_template(id)
        docs = self.sender.get_template_doc_files(id)
        fields = self.sender.get_template_fields(id)

        # Create new Template
        transient_ids = self.reciever.bulk_create_transient(docs)
        new_template = self.reciever.create_template(template_data, transient_ids)
        self.reciever.update_template_fields(new_template["id"], fields)

        return new_template["id"]

    def bulk_clone(self):
        # get all templates
        ids = []
        for id in ids:
            self.clone_template(id)


if __name__ == "__main__":
    load_dotenv()
    integration_key = os.getenv("INTEGRATION_KEY")
    base_uri = os.getenv("BASE_URI") + "api/rest/v6/"
    sign = Sign(integration_key, base_uri)

    template = "CBJCHBCAABAApwrYpRhhMqui0AVAW1WPkE6mcNWaBdfs"
    sender_email = "travis@houseofkrause.org"
    reciever = "travis@houseofkrause.org"

    sender = Sign(integration_key, base_uri, "travis@houseofkrause.org")
    reciever = Sign(integration_key, base_uri, "travis@houseofkrause.org")

    out = sign.clone_template(template, sender, reciever)

    print(out)
