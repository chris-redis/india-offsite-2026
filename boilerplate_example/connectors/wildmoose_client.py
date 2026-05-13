"""
WildMoose API client for executing playbook-based debugging agents.
Based on OpenAPI spec from wildmoose-sdk.

API Documentation: https://api.wildmoose.ai
Authentication: JWT Bearer token from Auth0
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import requests

from config import WildMooseConfig


class WildMooseClient:
    """Client for WildMoose Execution API."""

    def __init__(self):
        self.base_url = WildMooseConfig.BASE_URL.rstrip('/')
        self.api_token = WildMooseConfig.API_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        })

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to WildMoose API.
        
        Note: WildMoose doesn't have a health endpoint, so we validate
        the token format and return success if configured.
        """
        if not self.api_token:
            return {"success": False, "error": "No API token configured"}
        
        # Try a minimal request to validate the token
        # Using a dummy execution that should fail gracefully
        try:
            response = self.session.post(
                f"{self.base_url}/playbook/execution",
                json={"bookName": "__test_connection__", "time": datetime.utcnow().isoformat() + "Z"},
                timeout=10
            )
            # 400 = bad request (expected for invalid book)
            # 401 = unauthorized (bad token)
            # 403 = forbidden (API not enabled)
            if response.status_code == 401:
                return {"success": False, "error": "Authentication failed - invalid JWT token"}
            if response.status_code == 403:
                return {"success": False, "error": "API not enabled for organization"}
            # 400 or 200 means we authenticated successfully
            return {"success": True, "status": "connected"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def run_playbook(
        self,
        book_name: Optional[str] = None,
        message_link: Optional[str] = None,
        title: Optional[str] = None,
        time: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        details: Optional[str] = None,
        live_run: bool = False,
        channel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a playbook for investigating a production issue.

        Args:
            book_name: Name of the playbook to run (e.g., "perf-checks")
            message_link: Slack message link describing the issue
            title: Title of the alert/issue
            time: ISO 8601 datetime when the issue occurred
            attributes: Key-value pairs for issue context (host, environment, etc.)
            details: Additional details about the issue
            live_run: If True, sends results to incident management tool
            channel_id: Slack channel ID for posting results

        Returns:
            PlaybookExecutionResult with highlights, actionResults, etc.
        """
        payload = {}
        
        if book_name:
            payload["bookName"] = book_name
        if message_link:
            payload["messageLink"] = message_link
        if title:
            payload["title"] = title
        if time:
            payload["time"] = time
        if attributes:
            payload["attributes"] = attributes
        if details:
            payload["details"] = details
        if live_run:
            payload["liveRun"] = live_run
        if channel_id:
            payload["channelId"] = channel_id

        try:
            response = self.session.post(
                f"{self.base_url}/playbook/execution",
                json=payload,
                timeout=300  # Playbook execution can take time
            )
            response.raise_for_status()
            return {"success": True, "result": response.json()}
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            return {"success": False, "error": str(e), "detail": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def run_playbook_batch(
        self,
        input_list: List[Dict[str, Any]],
        live_run: bool = False,
        channel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute playbooks for multiple issues concurrently (max 10).

        Args:
            input_list: List of playbook execution inputs (max 10 items)
            live_run: If True, sends results to incident management tool
            channel_id: Slack channel ID for posting results

        Returns:
            List of PlaybookExecutionResult objects
        """
        if len(input_list) > 10:
            return {"success": False, "error": "Maximum 10 items per batch"}

        payload = {"inputList": input_list}
        if live_run:
            payload["liveRun"] = live_run
        if channel_id:
            payload["channelId"] = channel_id

        try:
            response = self.session.post(
                f"{self.base_url}/playbook/execution/batch",
                json=payload,
                timeout=600  # Batch can take longer
            )
            response.raise_for_status()
            return {"success": True, "results": response.json()}
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            return {"success": False, "error": str(e), "detail": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

