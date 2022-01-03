import os
from typing import Dict
import boto3
from datetime import datetime, timedelta

from functions.cost_explorer import CostExplorer
from functions.credential import Credential
from functions.slack import Slack

def daily(event: Dict[str, object], context: Dict[str, object]) -> None:
    cred = Credential(os.environ["SECRETS_MANAGER_ID"])
    slack = Slack(cred.slack_webhool_url)
    ce = CostExplorer(boto3.client('ce', region_name=os.environ["AWS_REGION"]))

    # Get previous day
    prev_day = datetime.strptime(event["time"], '%Y-%m-%dT%H:%M:%SZ').date() - timedelta(1)

    # Get cost report
    report = ce.daily_report(prev_day)

    # Post daily report to slack
    slack.post_daily_report(report)