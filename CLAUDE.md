# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

A scheduled AWS Lambda that runs daily at 08:00 UTC, scans active AWS regions for running infrastructure, feeds the results to Claude via AWS Bedrock, and posts a human-readable summary to Slack.

## Architecture

```
EventBridge (cron) → Lambda → scanner.py → Bedrock (Claude Haiku) → Slack Webhook
```

- `lambda/handler.py` — entry point; orchestrates scan → summarize → post to Slack
- `lambda/scanner.py` — calls AWS APIs per region; currently only EC2, but IAM allows RDS, Lambda, and ECS too
- `lambda/bedrock_client.py` — calls `bedrock:InvokeModel` with `anthropic.claude-3-haiku-20240307-v1:0` in `us-east-1`
- `terraform/` — provisions the Lambda, EventBridge rule, and IAM role

The Lambda must include `boto3` in the deployment zip because the AWS-managed runtime version may differ from what's needed. Dependencies are pinned in `lambda/requirements.txt`.

## Deployment Workflow

**Package and deploy:**
```bash
# Build the zip (from repo root)
cd lambda && pip install -r requirements.txt -t . && zip -r ../terraform/lambda.zip . -x ".venv/*" -x "__pycache__/*" -x "*.pyc" && cd ..

# Deploy
cd terraform
terraform init
terraform plan -var="slack_webhook_url=https://hooks.slack.com/..."
terraform apply -var="slack_webhook_url=https://hooks.slack.com/..."
```

**Secrets:** `slack_webhook_url` is sensitive and must be passed via `-var` or a `terraform.tfvars` file (gitignored). Never hardcode it.

## Local Testing

The Lambda has no test suite. To run locally, set up AWS credentials and invoke the scanner directly:

```bash
cd lambda
pip install -r requirements.txt
python -c "from scanner import scan_all_regions; import json; print(json.dumps(scan_all_regions(), indent=2))"
```

To test Bedrock summarization end-to-end, you need AWS credentials with `bedrock:InvokeModel` permission on `anthropic.claude-3-haiku-20240307-v1:0` in `us-east-1`.

## Key Constraints

- `scanner.py` currently limits scanning to `['us-east-1', 'eu-central-1']` — change to `ALL_REGIONS` to scan everywhere
- Bedrock model ID is hardcoded in both `bedrock_client.py` (the call) and `terraform/iam.tf` (the IAM resource ARN) — both must be updated together if the model changes
- The Lambda runtime in Terraform is `python3.12`; the local `.venv` uses `python3.10` — keep dependencies compatible with 3.12
- `response.json` at the repo root captures a prior run's error output; it's not used by the code
