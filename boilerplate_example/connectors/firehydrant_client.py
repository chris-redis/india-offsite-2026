"""
Firehydrant client for incident management.
Based on Firehydrant REST API documentation.
"""

import requests
from typing import Dict, Any, List, Optional
from config import FirehydrantConfig


class FirehydrantClient:
    """Client for interacting with Firehydrant API."""

    def __init__(self):
        self.base_url = FirehydrantConfig.BASE_URL.rstrip('/')
        self.api_token = FirehydrantConfig.API_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Firehydrant API."""
        try:
            response = self.session.get(
                f"{self.base_url}/ping",
                timeout=10
            )
            if response.status_code == 401:
                return {"success": False, "error": "Authentication failed - check API token"}
            response.raise_for_status()
            return {"success": True, "status": "connected"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_incidents(self, status: Optional[str] = None,
                      limit: int = 50) -> Dict[str, Any]:
        """
        Get incidents from Firehydrant.
        
        Args:
            status: Filter by status (open, closed, etc.)
            limit: Maximum number of incidents to return
        """
        try:
            params = {'per_page': limit}
            if status:
                params['status'] = status
            response = self.session.get(
                f"{self.base_url}/incidents",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "incidents": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        """Get a specific incident by ID."""
        try:
            response = self.session.get(
                f"{self.base_url}/incidents/{incident_id}",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "incident": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_services(self) -> Dict[str, Any]:
        """Get all services."""
        try:
            response = self.session.get(
                f"{self.base_url}/services",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "services": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_teams(self) -> Dict[str, Any]:
        """Get all teams."""
        try:
            response = self.session.get(
                f"{self.base_url}/teams",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "teams": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_environments(self) -> Dict[str, Any]:
        """Get all environments."""
        try:
            response = self.session.get(
                f"{self.base_url}/environments",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "environments": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_open_incidents(self) -> List[Dict]:
        """Get all open incidents."""
        result = self.get_incidents(status='open')
        return result.get('incidents', []) if result.get('success') else []

