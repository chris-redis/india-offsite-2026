"""
Glean AI client for chat and search functionality.
Based on CustomerStatus/GleanPOC projects.
"""

import json
import requests
from typing import Dict, Any, Optional, List
from config import GleanConfig


class GleanClient:
    """Client for interacting with Glean AI API."""

    def __init__(self):
        self.base_url = GleanConfig.BASE_URL.rstrip('/')
        self.api_token = GleanConfig.API_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Glean API."""
        try:
            # Try a simple chat request to test connectivity
            response = self.session.post(
                f"{self.base_url}/rest/api/v1/chat",
                json={
                    "stream": False,
                    "messages": [{"author": "USER", "fragments": [{"text": "hello"}]}]
                },
                timeout=30
            )
            if response.status_code == 401:
                return {"success": False, "error": "Authentication failed - check API token"}
            response.raise_for_status()
            return {"success": True, "status": "connected"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def chat(self, message: str, conversation_id: Optional[str] = None,
             include_citations: bool = True, stream: bool = True,
             timeout: int = 120) -> Dict[str, Any]:
        """
        Send a chat message to Glean AI.

        Args:
            message: The message to send
            conversation_id: Optional conversation ID for context
            include_citations: Whether to include source citations
            stream: Whether to use streaming mode (recommended for complete responses)
            timeout: Request timeout in seconds

        Returns:
            Chat response with answer and citations
        """
        payload = {
            "stream": stream,
            "messages": [
                {
                    "author": "USER",
                    "fragments": [{"text": message}]
                }
            ],
            "includeCitations": include_citations
        }
        if conversation_id:
            payload["conversationId"] = conversation_id

        try:
            response = self.session.post(
                f"{self.base_url}/rest/api/v1/chat",
                json=payload,
                timeout=timeout,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                # Process streaming response
                return self._process_streaming_response(response)
            else:
                return {"success": True, "response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def _process_streaming_response(self, response) -> Dict[str, Any]:
        """Process a streaming response from Glean and collect all text."""
        full_text = ""
        chat_id = None
        conversation_id = None
        citations = []

        for line in response.iter_lines():
            if line:
                try:
                    line_json = json.loads(line)

                    # Extract IDs
                    if chat_id is None and 'chatId' in line_json:
                        chat_id = line_json.get('chatId')
                    if conversation_id is None and 'conversationId' in line_json:
                        conversation_id = line_json.get('conversationId')

                    # Extract text from messages
                    messages = line_json.get('messages', [])
                    for message in messages:
                        if message.get('messageType') == 'CONTENT':
                            fragments = message.get('fragments', [])
                            for fragment in fragments:
                                text = fragment.get('text', '')
                                if isinstance(text, str):
                                    full_text += text

                                # Extract citations from fragments
                                if 'citations' in fragment:
                                    for citation in fragment['citations']:
                                        source_doc = citation.get('sourceDocument', {})
                                        citations.append({
                                            'title': source_doc.get('title', ''),
                                            'url': source_doc.get('url', ''),
                                            'snippet': citation.get('text', '')
                                        })
                except json.JSONDecodeError:
                    continue

        return {
            "success": True,
            "response": {
                "text": full_text.strip(),
                "chatId": chat_id,
                "conversationId": conversation_id,
                "citations": citations
            }
        }

    def search(self, query: str, page_size: int = 10,
               datasources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search Glean for documents and content.

        Args:
            query: Search query string
            page_size: Number of results to return
            datasources: Optional list of datasources to search

        Returns:
            Search results
        """
        payload = {
            "query": query,
            "pageSize": page_size
        }
        if datasources:
            payload["datasources"] = datasources

        try:
            response = self.session.post(
                f"{self.base_url}/rest/api/v1/search",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "results": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

