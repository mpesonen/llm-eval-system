#!/bin/bash
# Build Frontend for AWS Deployment
# Usage: ./build-frontend.sh <EC2_PUBLIC_IP_OR_DNS>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <EC2_PUBLIC_IP_OR_DNS> [S3_BUCKET_NAME]"
    echo ""
    echo "Examples:"
    echo "  $0 54.123.45.67"
    echo "  $0 ec2-54-123-45-67.compute-1.amazonaws.com my-llm-eval-bucket"
    exit 1
fi

EC2_HOST=$1
S3_BUCKET=${2:-}

# Navigate to web directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../web"

echo "=========================================="
echo "  Building Frontend for AWS"
echo "=========================================="
echo "API URL: http://$EC2_HOST:8000"
echo ""

# Build with the EC2 API URL
VITE_API_URL="http://$EC2_HOST:8000" npm run build

echo ""
echo "Build complete! Output in web/dist/"

# Upload to S3 if bucket name provided
if [ -n "$S3_BUCKET" ]; then
    echo ""
    echo "Uploading to S3 bucket: $S3_BUCKET"
    aws s3 sync dist/ "s3://$S3_BUCKET/" --delete
    echo ""
    echo "Upload complete!"
    echo "Frontend URL: http://$S3_BUCKET.s3-website-<region>.amazonaws.com"
else
    echo ""
    echo "To upload to S3, run:"
    echo "  aws s3 sync web/dist/ s3://YOUR_BUCKET_NAME/ --delete"
fi

echo ""
echo "Done!"
