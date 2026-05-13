# AWS-Bedrock-Daily

A scheduled AWS Lambda that scans your AWS infrastructure every morning, uses Claude (via AWS Bedrock) to generate a human-readable summary, and posts it to Slack.

## How It Works

```
EventBridge (daily 08:00 UTC) → Lambda → Scan AWS regions → Bedrock (Claude Haiku) → Slack
```

1. **EventBridge** triggers the Lambda on a daily cron schedule
2. **scanner.py** queries EC2 (and optionally RDS, Lambda, ECS) across regions
3. **bedrock_client.py** sends the scan data to `anthropic.claude-3-haiku-20240307-v1:0` in `us-east-1`
4. The AI-generated report is posted to a Slack channel via Incoming Webhook

## Prerequisites

- AWS account with Bedrock model access enabled for `anthropic.claude-3-haiku-20240307-v1:0` in `us-east-1`
- Slack Incoming Webhook URL
- Terraform >= 1.0
- Python 3.12

## Deployment

```bash
# 1. Package the Lambda
cd lambda
pip install -r requirements.txt -t .
zip -r ../terraform/lambda.zip . -x ".venv/*" -x "__pycache__/*" -x "*.pyc"
cd ..

# 2. Deploy with Terraform
cd terraform
terraform init
terraform apply -var="slack_webhook_url=https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

To pass variables without the CLI flag, create `terraform/terraform.tfvars` (gitignored):

```hcl
slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `aws_region` | `us-east-1` | Primary deployment region |
| `project_name` | `bedrock-scanner` | Prefix for all AWS resource names |
| `slack_webhook_url` | *(required)* | Slack Incoming Webhook URL |

To scan all AWS regions instead of the default two, edit `lambda/scanner.py` and replace the hardcoded list with `ALL_REGIONS`.

## IAM Permissions

The Lambda role is granted read-only access to EC2, RDS, Lambda, ECS, Bedrock (`InvokeModel`), and CloudWatch Logs.
