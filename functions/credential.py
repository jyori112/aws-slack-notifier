import os
import json

import boto3

def get_secrets(secret_id: str):
    session = boto3.session.Session()
    client = session.client('secretsmanager', region_name=os.environ["AWS_REGION"])
    secrets = client.get_secret_value(SecretId=secret_id)
    return json.loads(secrets["SecretString"])


class Credential:
    def __init__(self, secret_id: str):
        self.secrets = get_secrets(secret_id)

    @property
    def slack_webhool_url(self):
        return self.secrets["SLACK_WEBHOOK_URL"]