from typing import Dict

import requests

from functions.cost_explorer import DailyReport


class Slack:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def post(self, payload: Dict):
        requests.post(self.webhook_url, json=payload)

    def post_daily_report(self, report: DailyReport):
        # Format result
        text = '\n'.join(f'{service}: {price:.2f} USD' for service, price in sorted(report.costs.items(), key=lambda x: x[1], reverse=True))
        total_price = sum(price for _, price in report.costs.items())

        # Post to slack
        self.post({
            'attachments': [
                {
                    'color': '#36a64f',
                    'pretext': f'{report.date.strftime("%Y/%m/%d")}の請求額は、{total_price:.2f} USDです。',
                    'text': text
                }
            ]
        })