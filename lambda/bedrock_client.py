import boto3
import json

def generate_summary(scan_data: dict) -> str:
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    prompt = f"""You are a DevOps assistant. Here is a JSON scan of all AWS regions and their running resources:

{json.dumps(scan_data, indent=2)}

Generate a concise daily infrastructure report:
1. List each active region with its resources (use emojis: ✅ running, ⚠️ stopped, 💤 empty)
2. Highlight anything unusual (stopped instances, unused lambdas, etc.)
3. End with a 2-3 sentence AI summary and cost optimization tips

Keep it readable for Slack. Use bullet points."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=body
    )

    result = json.loads(response['body'].read())
    return result['content'][0]['text']