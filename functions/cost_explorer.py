from typing import Dict
from dataclasses import dataclass
from datetime import date, timedelta

import boto3
from functions.datetime_range import DatetimeRange

@dataclass(frozen=True)
class DailyReport:
    date: date
    costs: Dict[str, float]

class CostExplorer:
    def __init__(self, client: boto3.client):
        self.client = client

    def report(self, range: DatetimeRange):
        response = self.client.get_cost_and_usage(
            TimePeriod={
                'Start': range.start.strftime("%Y-%m-%d"),
                'End': range.end.strftime("%Y-%m-%d")
            },
            Granularity='MONTHLY',
            Metrics=[
                'AmortizedCost'
            ],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )

        return {item["Keys"][0]: float(item["Metrics"]["AmortizedCost"]["Amount"]) for item in response['ResultsByTime'][0]['Groups']}

    def daily_report(self, date: date):
        next_date = date + timedelta(1)
        costs = self.report(DatetimeRange(date, next_date))

        return DailyReport(date=date, costs=costs)