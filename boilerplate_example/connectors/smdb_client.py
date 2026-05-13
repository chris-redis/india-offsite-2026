"""
SMDB MySQL client for database queries.
Based on grafana/smdb_client.py from existing projects.

NOTE: Requires SSH tunnel to be running:
    ssh -L 3306:smdb.redislabs.com:3306 bastion
"""

import ssl
from typing import Dict, Any, List, Optional
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

from config import SMDBConfig


class SMDBClient:
    """Client for connecting to SMDB MySQL database."""

    def __init__(self):
        self.host = SMDBConfig.HOST
        self.port = SMDBConfig.PORT
        self.user = SMDBConfig.USER
        self.password = SMDBConfig.PASSWORD
        self.database = SMDBConfig.DATABASE
        self.cert_file = SMDBConfig.CERT_FILE
        self.key_file = SMDBConfig.KEY_FILE
        self._connection = None

    def _get_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure connection.

        SMDB requires SSL but does NOT require client certificates.
        The SSH tunnel handles the actual security, we just need SSL enabled.
        """
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Optionally load client certs if configured
        if self.cert_file and self.key_file:
            cert_path = Path(self.cert_file)
            key_path = Path(self.key_file)
            if cert_path.exists() and key_path.exists():
                ctx.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

        return ctx

    def connect(self) -> pymysql.Connection:
        """Establish database connection."""
        ssl_ctx = self._get_ssl_context()
        connect_args = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'cursorclass': DictCursor,
            'connect_timeout': 10,
            'ssl': ssl_ctx  # Always use SSL
        }

        self._connection = pymysql.connect(**connect_args)
        return self._connection

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to SMDB database."""
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 as connected")
                result = cursor.fetchone()
            conn.close()
            return {"success": True, "status": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def query(self, sql: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as list of dicts
        """
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
            conn.close()
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_customers(self, limit: int = 100) -> List[Dict]:
        """Get customer list from SMDB."""
        result = self.query(
            "SELECT * FROM customers LIMIT %s",
            (limit,)
        )
        return result.get("data", []) if result["success"] else []

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

