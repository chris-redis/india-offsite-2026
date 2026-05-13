"""
AWS client using boto3.
Provides common AWS service connections.
"""

from typing import Dict, Any, Optional
from config import AWSConfig

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class AWSClient:
    """Client for interacting with AWS services."""

    def __init__(self):
        self.access_key_id = AWSConfig.ACCESS_KEY_ID
        self.secret_access_key = AWSConfig.SECRET_ACCESS_KEY
        self.session_token = AWSConfig.SESSION_TOKEN
        self.region = AWSConfig.DEFAULT_REGION
        self._session = None

    def _get_session(self):
        """Get or create boto3 session."""
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is not installed. Run: pip install boto3")

        if self._session is None:
            session_kwargs = {
                'aws_access_key_id': self.access_key_id,
                'aws_secret_access_key': self.secret_access_key,
                'region_name': self.region
            }
            if self.session_token:
                session_kwargs['aws_session_token'] = self.session_token
            self._session = boto3.Session(**session_kwargs)
        return self._session

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to AWS by calling STS GetCallerIdentity."""
        if not BOTO3_AVAILABLE:
            return {"success": False, "error": "boto3 is not installed"}

        try:
            session = self._get_session()
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            return {
                "success": True,
                "status": {
                    "account": identity.get('Account'),
                    "arn": identity.get('Arn'),
                    "user_id": identity.get('UserId')
                }
            }
        except NoCredentialsError:
            return {"success": False, "error": "No AWS credentials found"}
        except ClientError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_client(self, service_name: str, region: Optional[str] = None):
        """
        Get a boto3 client for a specific AWS service.
        
        Args:
            service_name: AWS service name (e.g., 's3', 'ec2', 'lambda')
            region: Optional region override
            
        Returns:
            boto3 client for the service
        """
        session = self._get_session()
        return session.client(service_name, region_name=region or self.region)

    def get_resource(self, service_name: str, region: Optional[str] = None):
        """
        Get a boto3 resource for a specific AWS service.
        
        Args:
            service_name: AWS service name (e.g., 's3', 'ec2', 'dynamodb')
            region: Optional region override
            
        Returns:
            boto3 resource for the service
        """
        session = self._get_session()
        return session.resource(service_name, region_name=region or self.region)

    def list_s3_buckets(self) -> Dict[str, Any]:
        """List all S3 buckets."""
        try:
            s3 = self.get_client('s3')
            response = s3.list_buckets()
            buckets = [b['Name'] for b in response.get('Buckets', [])]
            return {"success": True, "buckets": buckets}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_ec2_instances(self, region: Optional[str] = None) -> Dict[str, Any]:
        """List EC2 instances in a region."""
        try:
            ec2 = self.get_client('ec2', region)
            response = ec2.describe_instances()
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append({
                        'id': instance.get('InstanceId'),
                        'type': instance.get('InstanceType'),
                        'state': instance.get('State', {}).get('Name'),
                        'name': next(
                            (t['Value'] for t in instance.get('Tags', []) if t['Key'] == 'Name'),
                            None
                        )
                    })
            return {"success": True, "instances": instances}
        except Exception as e:
            return {"success": False, "error": str(e)}

