import sys
sys.path.append('.')

from app.core.config import settings
import boto3

print("Checking AWS credentials...")
print(f"Region: {settings.AWS_REGION}")
print(f"Access Key: {settings.AWS_ACCESS_KEY_ID[:10]}..." if settings.AWS_ACCESS_KEY_ID else "Access Key: None")
print(f"Has Session Token: {bool(settings.AWS_SESSION_TOKEN)}")

try:
    # Test credentials with STS
    sts = boto3.client(
        'sts',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token=settings.AWS_SESSION_TOKEN,
        region_name=settings.AWS_REGION
    )
    
    identity = sts.get_caller_identity()
    print(f"\n✓ Credentials are valid!")
    print(f"Account: {identity['Account']}")
    print(f"User: {identity['Arn']}")
    
except Exception as e:
    print(f"\n✗ Credentials are INVALID or EXPIRED")
    print(f"Error: {e}")
    print("\nPlease refresh your AWS credentials:")
    print("1. Go to AWS Console")
    print("2. Click your username → 'Command line or programmatic access'")
    print("3. Copy new credentials")
    print("4. Update .env file")
