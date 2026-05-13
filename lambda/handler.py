import json
import os
import boto3
import urllib.request
from datetime import datetime
from scanner import scan_all_regions
from bedrock_client import generate_summary

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def lambda_handler(event, context):
    print("Starting AWS infrastructure scan...")

    # Step 1: Scan all regions
    scan_data = scan_all_regions()
    print(f"Scanned {len(scan_data)} active regions")

    # Step 2: Generate AI summary via Bedrock
    summary = generate_summary(scan_data)

    # Step 3: Send to Slack
    date_str = datetime.now().strftime('%B %d, %Y')
    message = {
        "text": f"🌍 *AWS Daily Infrastructure Report — {date_str}*\n\n{summary}"
    }
    data = json.dumps(message).encode('utf-8')
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)

    return {'statusCode': 200, 'body': 'Report sent successfully'}