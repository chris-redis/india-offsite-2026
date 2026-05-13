"""
Cloud Exporter client for Redis Cloud cluster information.
Based on grafana/cloud_exporter_client.py from existing projects.
"""

import ssl
import json
import urllib.request
from typing import Dict, Any, Optional
from pathlib import Path

from config import CloudExporterConfig


class CloudExporterClient:
    """Client for interacting with Cloud Exporter API."""

    def __init__(self):
        self.url = CloudExporterConfig.URL
        self.cert_file = CloudExporterConfig.CERT_FILE
        self.key_file = CloudExporterConfig.KEY_FILE

    def _get_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with client certificates."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if self.cert_file and self.key_file:
            cert_path = Path(self.cert_file)
            key_path = Path(self.key_file)
            if cert_path.exists() and key_path.exists():
                ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

        return ctx

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Cloud Exporter API."""
        try:
            ctx = self._get_ssl_context()
            req = urllib.request.Request(self.url)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                # Just check if we got valid JSON response
                return {"success": True, "status": f"Retrieved {len(data) if isinstance(data, list) else 1} records"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cluster_info(self, data_type: str = "cluster_info") -> Dict[str, Any]:
        """
        Get cluster information from Cloud Exporter.
        
        Args:
            data_type: Type of data to retrieve (cluster_info, etc.)
            
        Returns:
            Cluster data as dict
        """
        url = self.url.split('?')[0] + f"?data_type={data_type}"
        try:
            ctx = self._get_ssl_context()
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
                return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_clusters(self) -> Dict[str, Any]:
        """Get all cluster information."""
        return self.get_cluster_info("cluster_info")

    def get_cluster_by_id(self, cluster_id: int) -> Optional[Dict]:
        """
        Get specific cluster by ID.
        
        Args:
            cluster_id: The cluster ID to find
            
        Returns:
            Cluster data or None if not found
        """
        result = self.get_all_clusters()
        if not result["success"]:
            return None

        clusters = result.get("data", [])
        for cluster in clusters:
            if cluster.get("cluster_id") == cluster_id:
                return cluster
        return None

