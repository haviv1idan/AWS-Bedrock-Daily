variable "aws_region" {
  description = "Primary AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  default     = "bedrock-scanner"
}

variable "slack_webhook_url" {
  description = "Slack Incoming Webhook URL"
  type        = string
  sensitive   = true
}