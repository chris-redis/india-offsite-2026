"""
Jira API client for issue tracking and project management.
Based on SupportTicketAnalysis/jira_cmdb_lookup.py from existing projects.

Uses Atlassian REST API v3.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

from config import JiraConfig


class JiraClient:
    """Client for Jira REST API."""

    def __init__(self):
        self.base_url = JiraConfig.URL.rstrip('/')
        self.user = JiraConfig.USER
        self.api_token = JiraConfig.API_TOKEN
        self.auth = HTTPBasicAuth(self.user, self.api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Jira API."""
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/myself",
                timeout=10
            )
            if response.status_code == 401:
                return {"success": False, "error": "Authentication failed - check credentials"}
            response.raise_for_status()
            user_info = response.json()
            return {
                "success": True,
                "status": "connected",
                "user": user_info.get("displayName", user_info.get("emailAddress"))
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 50,
        start_at: int = 0
    ) -> Dict[str, Any]:
        """
        Search for issues using JQL (Jira Query Language).

        Args:
            jql: JQL query string
            fields: List of fields to return (default: summary, status, created)
            max_results: Maximum number of results (default: 50)
            start_at: Starting index for pagination (default: 0)

        Returns:
            Dict with issues list and pagination info
        """
        if fields is None:
            fields = ["summary", "status", "created", "updated", "issuetype", "priority"]

        params = {
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": ",".join(fields)
        }

        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/search/jql",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "result": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a specific issue by key.

        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            fields: List of fields to return (default: all)

        Returns:
            Issue details
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "issue": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_projects(self) -> Dict[str, Any]:
        """Get list of accessible projects."""
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/project",
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "projects": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue.

        Args:
            project_key: Project key (e.g., "PROJ")
            summary: Issue summary/title
            issue_type: Issue type (Task, Bug, Story, etc.)
            description: Issue description
            priority: Priority name
            labels: List of labels
            custom_fields: Dict of custom field IDs to values

        Returns:
            Created issue details
        """
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }

        if description:
            # Atlassian Document Format (ADF) for description
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            }
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = labels
        if custom_fields:
            fields.update(custom_fields)

        try:
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue",
                json={"fields": fields},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "issue": response.json()}
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response else str(e)
            return {"success": False, "error": str(e), "detail": error_detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

