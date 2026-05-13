"""
GCP client using google-cloud libraries.
Provides common GCP service connections.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from config import GCPConfig

try:
    from google.cloud import storage
    from google.cloud import compute_v1
    from google.auth import default as google_auth_default
    from google.auth.exceptions import DefaultCredentialsError
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False


class GCPClient:
    """Client for interacting with GCP services."""

    def __init__(self):
        self.credentials_file = GCPConfig.CREDENTIALS_FILE
        self.project_id = GCPConfig.PROJECT_ID
        self._credentials = None
        self._project = None

        # Set credentials file in environment if provided
        if self.credentials_file and Path(self.credentials_file).exists():
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_file

    def _get_credentials(self):
        """Get GCP credentials."""
        if not GCP_AVAILABLE:
            raise ImportError("google-cloud libraries not installed. Run: pip install google-cloud-storage google-cloud-compute")

        if self._credentials is None:
            try:
                self._credentials, self._project = google_auth_default()
                if self.project_id:
                    self._project = self.project_id
            except DefaultCredentialsError as e:
                raise RuntimeError(f"Failed to get GCP credentials: {e}")

        return self._credentials, self._project

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to GCP by listing storage buckets."""
        if not GCP_AVAILABLE:
            return {"success": False, "error": "google-cloud libraries not installed"}

        try:
            credentials, project = self._get_credentials()
            client = storage.Client(credentials=credentials, project=project)
            # Just try to list buckets (limited to 1) to test connection
            buckets = list(client.list_buckets(max_results=1))
            return {
                "success": True,
                "status": {
                    "project": project,
                    "authenticated": True
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_storage_client(self):
        """Get GCP Storage client."""
        credentials, project = self._get_credentials()
        return storage.Client(credentials=credentials, project=project)

    def list_buckets(self) -> Dict[str, Any]:
        """List all GCS buckets."""
        try:
            client = self.get_storage_client()
            buckets = [b.name for b in client.list_buckets()]
            return {"success": True, "buckets": buckets}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_compute_instances(self, zone: Optional[str] = None) -> Dict[str, Any]:
        """
        List Compute Engine instances.
        
        Args:
            zone: Optional zone filter (e.g., 'us-central1-a')
        """
        if not GCP_AVAILABLE:
            return {"success": False, "error": "google-cloud-compute not installed"}

        try:
            credentials, project = self._get_credentials()
            client = compute_v1.InstancesClient(credentials=credentials)

            instances = []
            if zone:
                request = compute_v1.ListInstancesRequest(project=project, zone=zone)
                for instance in client.list(request=request):
                    instances.append({
                        'name': instance.name,
                        'zone': zone,
                        'status': instance.status,
                        'machine_type': instance.machine_type.split('/')[-1]
                    })
            else:
                # List instances across all zones
                agg_client = compute_v1.InstancesClient(credentials=credentials)
                request = compute_v1.AggregatedListInstancesRequest(project=project)
                for zone_name, response in agg_client.aggregated_list(request=request):
                    if response.instances:
                        for instance in response.instances:
                            instances.append({
                                'name': instance.name,
                                'zone': zone_name.split('/')[-1],
                                'status': instance.status,
                                'machine_type': instance.machine_type.split('/')[-1]
                            })

            return {"success": True, "instances": instances}
        except Exception as e:
            return {"success": False, "error": str(e)}

