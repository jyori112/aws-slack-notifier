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
        sorted_costs = sorted(report.costs.items(), key=lambda x: x[1], reverse=True)

        services, costs = zip(*sorted_costs)
        total_price = sum(price for _, price in report.costs.items())

        # Post to slack
        payload = {
            "username": "AWS Cost Notification",
            "icon_emoji": ":aws:",
            "attachments": [
                {
                    "color": "#36a64f",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Total Price:* {total_price:.2f} USD"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Service:*\n" + "\n".join(f"{service}:" for service in services)
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Cost:*\n" + "\n".join(f"{cost:.2f} USD" for cost in costs)
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.post(payload)