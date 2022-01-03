import os
from typing import Dict, Tuple
import boto3
import json
import requests
from datetime import datetime, timedelta, date

from functions.cost_explorer import CostExplorer
from functions.datetime_range import DatetimeRange
from functions.credential import Credential

from .slack import Slack

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def daily(event: Dict[str, object], context: Dict[str, object]) -> None:
    cred = Credential(os.environ["SECRETS_MANAGER_ID"])
    slack = Slack(cred.slack_webhool_url)
    ce = CostExplorer(boto3.client('ce', region_name=os.environ["AWS_REGION"]))

    # Get Datetime Range to retrieve cost information
    this_day = datetime.strptime(event["time"], '%Y-%m-%dT%H:%M:%SZ').replace(hour=0, minute=0, second=0, microsecond=0)
    prev_day = this_day - timedelta(1)
    datetime_range = DatetimeRange(prev_day, this_day)

    # Get cost report
    report = ce.report(datetime_range)

    # Format result
    text = '\n'.join(f'{service}: {price:.2f} USD' for service, price in sorted(report.items(), key=lambda x: x[1], reverse=True))
    total_price = sum(price for _, price in report.items())

    # Post to slack
    slack.post({
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': f'{prev_day.strftime("%Y/%m/%d")}の請求額は、{total_price:.2f} USDです。',
                'text': text
            }
        ]
    })

def main(event, context) -> None:
    print("running")
    client = boto3.client('ce', region_name='us-east-1')

    # 合計とサービス毎の請求額を取得する
    total_billing = get_total_billing(client)
    service_billings = get_service_billings(client)

    # Slack用のメッセージを作成して投げる
    (title, detail) = get_message(total_billing, service_billings)
    post_slack(title, detail)


def get_total_billing(client) -> dict:
    (start_date, end_date) = get_total_cost_date_range()

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ]
    )
    return {
        'start': response['ResultsByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'],
    }


def get_service_billings(client) -> list:
    (start_date, end_date) = get_total_cost_date_range()

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
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

    billings = []

    for item in response['ResultsByTime'][0]['Groups']:
        billings.append({
            'service_name': item['Keys'][0],
            'billing': item['Metrics']['AmortizedCost']['Amount']
        })
    return billings


def get_message(total_billing: dict, service_billings: list) -> Tuple[str, str]:
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')

    # Endの日付は結果に含まないため、表示上は前日にしておく
    end_today = datetime.strptime(total_billing['end'], '%Y-%m-%d')
    end_yesterday = (end_today - timedelta(days=1)).strftime('%m/%d')

    total = round(float(total_billing['billing']), 2)

    title = f'{start}～{end_yesterday}の請求額は、{total:.2f} USDです。'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            # 請求無し（0.0 USD）の場合は、内訳を表示しない
            continue
        details.append(f'　・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)


def post_slack(title: str, detail: str) -> None:
    # https://api.slack.com/incoming-webhooks
    # https://api.slack.com/docs/message-formatting
    # https://api.slack.com/docs/messages/builder
    payload = {
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': title,
                'text': detail
            }
        ]
    }

    # http://requests-docs-ja.readthedocs.io/en/latest/user/quickstart/
    try:
        print(payload)
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)


def get_total_cost_date_range() -> Tuple[str, str]:
    start_date = get_begin_of_month()
    end_date = get_today()

    # get_cost_and_usage()のstartとendに同じ日付は指定不可のため、
    # 「今日が1日」なら、「先月1日から今月1日（今日）」までの範囲にする
    if start_date == end_date:
        end_of_month = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=-1)
        begin_of_month = end_of_month.replace(day=1)
        return begin_of_month.date().isoformat(), end_date
    return start_date, end_date


def get_begin_of_month() -> str:
    return date.today().replace(day=1).isoformat()


def get_prev_day(prev: int) -> str:
    return (date.today() - timedelta(days=prev)).isoformat()

def get_today() -> str:
    return date.today().isoformat()
