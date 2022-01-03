import boto3
from functions.datetime_range import DatetimeRange


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