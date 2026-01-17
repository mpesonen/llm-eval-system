# AWS Deployment Guide

Deploy the LLM Eval System to AWS with EC2 (backend) and S3 (frontend).

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │────────▶│  S3 Bucket  │         │    EC2      │
│             │         │  (Frontend) │────────▶│  (Backend)  │
└─────────────┘         └─────────────┘         └─────────────┘
                         Static React           FastAPI + uvicorn
                         Dashboard              Port 8000
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (`aws configure`)
- SSH key pair for EC2 access

## Step 1: Launch EC2 Instance

### Via AWS Console

1. Go to **EC2 → Launch Instance**
2. Configure:
   - **Name**: `llm-eval-api`
   - **AMI**: Amazon Linux 2023 or Ubuntu 22.04
   - **Instance type**: `t3.micro` (free tier) or `t3.small`
   - **Key pair**: Select or create one
   - **Network**: Default VPC, public subnet
   - **Security Group**: Create new with rules:
     - SSH (22) from your IP
     - Custom TCP (8000) from anywhere (0.0.0.0/0)
   - **Storage**: 8 GB gp3 (default)
3. Click **Launch Instance**

### Via AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
  --group-name llm-eval-sg \
  --description "LLM Eval API security group"

# Add SSH rule
aws ec2 authorize-security-group-ingress \
  --group-name llm-eval-sg \
  --protocol tcp --port 22 --cidr YOUR_IP/32

# Add API rule
aws ec2 authorize-security-group-ingress \
  --group-name llm-eval-sg \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0

# Launch instance (Amazon Linux 2023)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name YOUR_KEY_NAME \
  --security-groups llm-eval-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=llm-eval-api}]'
```

## Step 2: Set Up EC2 Instance

### SSH into the instance

```bash
# Amazon Linux
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Ubuntu
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Run the setup script

```bash
# Clone the repository first
git clone https://github.com/YOUR_USERNAME/llm-eval-system.git
cd llm-eval-system

# Run setup
chmod +x deploy/ec2-setup.sh
./deploy/ec2-setup.sh
```

Or run directly from the repo:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/llm-eval-system/main/deploy/ec2-setup.sh | bash
```

### Configure API keys

```bash
# Edit the environment file
nano /opt/llm-eval/.env

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-key-here
```

### Start the service

```bash
sudo systemctl start llm-eval
sudo systemctl status llm-eval

# View logs
sudo journalctl -u llm-eval -f
```

### Verify the API is running

```bash
curl http://localhost:8000/api/runs
```

## Step 3: Create S3 Bucket for Frontend

### Via AWS Console

1. Go to **S3 → Create bucket**
2. Configure:
   - **Bucket name**: `llm-eval-dashboard` (must be globally unique)
   - **Region**: Same as EC2
   - **Block Public Access**: Uncheck "Block all public access"
   - Acknowledge the warning
3. Click **Create bucket**

### Enable Static Website Hosting

1. Go to bucket → **Properties** tab
2. Scroll to **Static website hosting** → Edit
3. Enable and set:
   - Index document: `index.html`
   - Error document: `index.html`
4. Save changes

### Set Bucket Policy

1. Go to bucket → **Permissions** tab
2. Edit **Bucket policy** and add:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

## Step 4: Build and Deploy Frontend

### Build with EC2 API URL

```bash
# From the project root
chmod +x deploy/build-frontend.sh
./deploy/build-frontend.sh YOUR_EC2_PUBLIC_IP
```

### Upload to S3

```bash
# Sync the built files to S3
aws s3 sync web/dist/ s3://YOUR_BUCKET_NAME/ --delete
```

Or use the build script with S3 upload:

```bash
./deploy/build-frontend.sh YOUR_EC2_PUBLIC_IP YOUR_BUCKET_NAME
```

## Step 5: Access Your Dashboard

The frontend URL will be:
```
http://YOUR_BUCKET_NAME.s3-website-REGION.amazonaws.com
```

For example:
```
http://llm-eval-dashboard.s3-website-us-east-1.amazonaws.com
```

## Running Evaluations

SSH into your EC2 instance and run evaluations:

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
cd /opt/llm-eval

# Run all suites
uv run python llm_eval.py --all-suites

# Run a specific suite
uv run python llm_eval.py --suite datasets/examples/basic.yaml
```

## Troubleshooting

### API not responding

```bash
# Check if service is running
sudo systemctl status llm-eval

# Check logs
sudo journalctl -u llm-eval -n 50

# Restart service
sudo systemctl restart llm-eval
```

### CORS errors in browser

The FastAPI backend already has CORS configured. Make sure you're using the correct EC2 public IP/DNS in the frontend build.

### S3 website not loading

1. Verify bucket policy allows public read
2. Check static website hosting is enabled
3. Ensure index.html exists in the bucket

## Costs

Estimated monthly costs (US East region):

| Resource | Cost |
|----------|------|
| EC2 t3.micro | ~$8.50/month (or free tier) |
| S3 storage (< 1GB) | ~$0.02/month |
| S3 requests | ~$0.01/month |
| **Total** | **~$8-10/month** |

## Cleanup

To avoid ongoing charges:

```bash
# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID

# Delete S3 bucket contents and bucket
aws s3 rm s3://YOUR_BUCKET_NAME --recursive
aws s3 rb s3://YOUR_BUCKET_NAME

# Delete security group
aws ec2 delete-security-group --group-name llm-eval-sg
```
