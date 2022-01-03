from typing import Dict

import requests


class Slack:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def post(self, payload: Dict):
        requests.post(self.webhook_url, json=payload)