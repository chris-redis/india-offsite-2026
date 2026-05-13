"""
Squadcast client for incident management.
Based on squadcast/squadcast/squadcast.py from existing projects.
"""

import requests
from typing import Dict, Any, List, Optional
from config import SquadcastConfig


class SquadcastClient:
    """Client for interacting with Squadcast API."""

    def __init__(self):
        self.bearer_token = SquadcastConfig.BEARER_TOKEN
        self.auth_url = SquadcastConfig.AUTH_URL
        self.url_teams = SquadcastConfig.URL_TEAMS
        self.url_services = SquadcastConfig.URL_SERVICES
        self.url_incidents = SquadcastConfig.URL_INCIDENTS
        self._access_token = None
        self.session = requests.Session()

    def _get_access_token(self) -> str:
        """Get access token using refresh token."""
        if self._access_token:
            return self._access_token

        headers = {
            'X-Refresh-Token': self.bearer_token,
            'Content-Type': 'application/json'
        }
        response = self.session.get(self.auth_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        self._access_token = data.get('data', {}).get('access_token')
        return self._access_token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with access token."""
        token = self._get_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Squadcast API."""
        try:
            headers = self._get_headers()
            response = self.session.get(
                self.url_teams,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "status": "connected"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_teams(self) -> Dict[str, Any]:
        """Get all teams."""
        try:
            headers = self._get_headers()
            response = self.session.get(self.url_teams, headers=headers, timeout=10)
            response.raise_for_status()
            return {"success": True, "teams": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_services(self, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Get services, optionally filtered by team."""
        try:
            headers = self._get_headers()
            url = self.url_services
            if team_id:
                url = f"{url}?owner_id={team_id}"
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return {"success": True, "services": response.json().get('data', [])}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_incidents(self, status: Optional[str] = None,
                      limit: int = 50) -> Dict[str, Any]:
        """
        Get incidents.

        Args:
            status: Filter by status (triggered, acknowledged, resolved)
            limit: Maximum number of incidents to return
        """
        try:
            headers = self._get_headers()
            params = {'limit': limit}
            if status:
                params['status'] = status
            response = self.session.get(
                self.url_incidents,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json().get('data', {})
            # Handle nested structure: data.incidents contains the actual list
            if isinstance(data, dict) and 'incidents' in data:
                incidents = data.get('incidents', [])
            else:
                incidents = data if isinstance(data, list) else []
            return {"success": True, "incidents": incidents}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_open_incidents(self) -> List[Dict]:
        """Get all open (triggered + acknowledged) incidents."""
        triggered = self.get_incidents(status='triggered')
        acknowledged = self.get_incidents(status='acknowledged')
        incidents = []
        if triggered.get('success'):
            incidents.extend(triggered.get('incidents', []))
        if acknowledged.get('success'):
            incidents.extend(acknowledged.get('incidents', []))
        return incidents

