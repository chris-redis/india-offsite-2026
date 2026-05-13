"""
Redis Knowledge Base - Glean-powered contextual information for Redis and Redis Cloud.

This module provides a high-level interface for querying Redis-specific knowledge
through Glean. It should be used by AI assistants and applications to gather
contextual information about Redis products, architecture, troubleshooting, and
internal processes.

Usage:
    from connectors import RedisKnowledge
    
    kb = RedisKnowledge()
    
    # Ask a question about Redis Cloud
    answer = kb.ask("How do I configure Active-Active replication?")
    
    # Search for documentation
    docs = kb.search_docs("CRDB conflict resolution")
    
    # Get troubleshooting help
    help = kb.troubleshoot("high latency on Redis Cloud cluster")
"""

from typing import Dict, Any, Optional, List
from .glean_client import GleanClient
from config import GleanConfig


class RedisKnowledge:
    """
    Redis-specific knowledge base powered by Glean.
    
    This class provides convenience methods for querying Redis and Redis Cloud
    information from Glean's indexed knowledge base, which includes:
    - Internal documentation and runbooks
    - Confluence pages
    - Slack conversations
    - Jira tickets
    - Code repositories
    - And other indexed sources
    """

    def __init__(self):
        self.client = GleanClient()
        self._conversation_id = None

    @classmethod
    def is_configured(cls) -> bool:
        """Check if Glean is configured and available."""
        return GleanConfig.validate()

    def ask(
        self,
        question: str,
        context: Optional[str] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a question about Redis or Redis Cloud.
        
        Args:
            question: The question to ask
            context: Optional additional context to include
            include_sources: Whether to include source citations
            
        Returns:
            Dict with 'answer', 'sources', and 'success' keys
        """
        # Build the query with optional context
        if context:
            full_query = f"Context: {context}\n\nQuestion: {question}"
        else:
            full_query = question

        result = self.client.chat(
            message=full_query,
            conversation_id=self._conversation_id,
            include_citations=include_sources
        )

        if not result.get("success"):
            return result

        response = result.get("response", {})
        
        # Extract the answer text from the response
        answer = self._extract_answer(response)
        sources = self._extract_sources(response) if include_sources else []
        
        # Store conversation ID for follow-up questions
        self._conversation_id = response.get("conversationId")

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "conversation_id": self._conversation_id
        }

    def search_docs(
        self,
        query: str,
        max_results: int = 10,
        datasources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for Redis-related documentation.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            datasources: Optional list of specific datasources to search
            
        Returns:
            Dict with search results
        """
        return self.client.search(
            query=query,
            page_size=max_results,
            datasources=datasources
        )

    def troubleshoot(self, issue_description: str) -> Dict[str, Any]:
        """
        Get troubleshooting guidance for a Redis-related issue.
        
        Args:
            issue_description: Description of the issue
            
        Returns:
            Troubleshooting guidance with relevant runbooks and documentation
        """
        prompt = f"""I need help troubleshooting a Redis/Redis Cloud issue.

Issue: {issue_description}

Please provide:
1. Possible root causes
2. Diagnostic steps to identify the issue
3. Recommended solutions or workarounds
4. Links to relevant runbooks or documentation if available"""

        return self.ask(prompt, include_sources=True)

    def explain_concept(self, concept: str) -> Dict[str, Any]:
        """
        Get an explanation of a Redis concept or feature.
        
        Args:
            concept: The concept to explain (e.g., "Active-Active", "RediSearch")
            
        Returns:
            Explanation with relevant documentation
        """
        prompt = f"""Explain the following Redis/Redis Cloud concept: {concept}

Please include:
1. What it is and how it works
2. Common use cases
3. Any important considerations or limitations
4. Links to documentation if available"""

        return self.ask(prompt, include_sources=True)

    def get_runbook(self, topic: str) -> Dict[str, Any]:
        """
        Search for runbooks related to a topic.

        Args:
            topic: The topic to find runbooks for

        Returns:
            Relevant runbooks and procedures
        """
        prompt = f"""Find runbooks or operational procedures related to: {topic}

Please provide links to relevant runbooks and summarize the key steps."""

        return self.ask(prompt, include_sources=True)

    def customer_context(self, customer_name: str, issue: Optional[str] = None) -> Dict[str, Any]:
        """
        Gather context about a customer and their Redis Cloud setup.

        Args:
            customer_name: Customer name or identifier
            issue: Optional specific issue to focus on

        Returns:
            Customer context and relevant information
        """
        if issue:
            prompt = f"""Gather context about customer "{customer_name}" related to: {issue}

Look for:
1. Recent tickets or issues
2. Their Redis Cloud configuration
3. Any known ongoing problems
4. Relevant Slack discussions"""
        else:
            prompt = f"""Gather context about customer "{customer_name}".

Look for:
1. Their Redis Cloud setup and configuration
2. Recent support tickets
3. Any known issues or escalations
4. Account information"""

        return self.ask(prompt, include_sources=True)

    def reset_conversation(self):
        """Reset the conversation context for a fresh start."""
        self._conversation_id = None

    def _extract_answer(self, response: Dict[str, Any]) -> str:
        """Extract the answer text from a Glean response."""
        # New streaming format - text is directly in response
        if "text" in response:
            return response["text"]

        # Handle different response formats (legacy non-streaming)
        if "messages" in response:
            for msg in response.get("messages", []):
                if msg.get("author") == "GLEAN_AI":
                    fragments = msg.get("fragments", [])
                    return "".join(f.get("text", "") for f in fragments)

        # Fallback to other possible formats
        if "answer" in response:
            return response["answer"]

        return str(response)

    def _extract_sources(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract source citations from a Glean response."""
        sources = []

        # New streaming format - citations are directly in response
        citations = response.get("citations", [])
        for citation in citations:
            source = {
                "title": citation.get("title", ""),
                "url": citation.get("url", ""),
                "snippet": citation.get("snippet", "")
            }
            if source["title"] or source["url"]:
                sources.append(source)

        # Also check for sources in messages (legacy format)
        for msg in response.get("messages", []):
            for fragment in msg.get("fragments", []):
                if "citations" in fragment:
                    for citation in fragment["citations"]:
                        source = {
                            "title": citation.get("sourceDocument", {}).get("title", ""),
                            "url": citation.get("sourceDocument", {}).get("url", ""),
                            "snippet": citation.get("text", "")
                        }
                        if source["title"] or source["url"]:
                            sources.append(source)

        return sources

