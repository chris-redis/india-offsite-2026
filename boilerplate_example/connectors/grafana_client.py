"""
Grafana/Prometheus client for querying metrics.
Based on grafana/main.py from existing projects.
"""

import requests
from typing import Optional, Dict, Any, List
from config import GrafanaConfig


class GrafanaClient:
    """Client for interacting with Grafana/Prometheus API."""

    def __init__(self):
        self.url = GrafanaConfig.URL
        self.api_token = GrafanaConfig.API_TOKEN
        self.datasource_uid = GrafanaConfig.PROM_DATASOURCE_UID
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })

    def test_connection(self) -> Dict[str, Any]:
        """Test connectivity to Grafana API."""
        try:
            response = self.session.get(
                f"{self.url}/api/health",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "status": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def query_prometheus(self, query: str, start: Optional[str] = None,
                         end: Optional[str] = None, step: str = "1m") -> Dict[str, Any]:
        """
        Execute a PromQL query against Grafana's Prometheus datasource.

        Args:
            query: PromQL query string
            start: Start time (ISO format or relative like 'now-1h')
            end: End time (ISO format or relative like 'now')
            step: Query resolution step

        Returns:
            Query results as dict
        """
        payload = {
            "queries": [{
                "refId": "A",
                "datasource": {"uid": self.datasource_uid},
                "expr": query,
                "instant": False,
                "range": True,
                "intervalMs": 60000,
                "maxDataPoints": 1000
            }],
            "from": start or "now-1h",
            "to": end or "now"
        }

        try:
            response = self.session.post(
                f"{self.url}/api/ds/query",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def query_prometheus_batch(
        self,
        queries: Dict[str, str],
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple PromQL queries in a single API call.

        Args:
            queries: Dict mapping refId/name to PromQL query string
            start: Start time (ISO format or relative like 'now-1h')
            end: End time (ISO format or relative like 'now')

        Returns:
            Query results as dict with results keyed by refId
        """
        query_list = []
        for ref_id, expr in queries.items():
            query_list.append({
                "refId": ref_id,
                "datasource": {"uid": self.datasource_uid},
                "expr": expr,
                "instant": False,
                "range": True,
                "intervalMs": 60000,
                "maxDataPoints": 100  # Reduced for batch queries
            })

        payload = {
            "queries": query_list,
            "from": start or "now-1h",
            "to": end or "now"
        }

        try:
            response = self.session.post(
                f"{self.url}/api/ds/query",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_datasources(self) -> Dict[str, Any]:
        """Get list of configured datasources."""
        try:
            response = self.session.get(
                f"{self.url}/api/datasources",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "datasources": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def get_cluster_metrics(
        self,
        cluster_fqdn: str,
        time_range: str = "5m",
        metrics: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Get key metrics for a Redis Cloud cluster.

        Args:
            cluster_fqdn: Cluster FQDN (e.g., "c42998.us-east-1-mz.ec2.cloud.rlrcp.com")
            time_range: Time range to query (e.g., "5m", "1h", "24h")
            metrics: Optional list of specific metrics to query. If None, queries all default metrics.

        Returns:
            Dict with cluster metrics organized by database
        """
        # Default metrics to query
        default_metrics = {
            "connections": "bdb_conns",
            "ops_per_sec": "bdb_instantaneous_ops_per_sec",
            "used_memory_bytes": "bdb_used_memory",
            "avg_latency_sec": "bdb_avg_latency",
            "egress_bytes_per_sec": "rate(bdb_egress_bytes[1m])",
            "ingress_bytes_per_sec": "rate(bdb_ingress_bytes[1m])",
            "read_hits": "bdb_read_hits",
            "read_misses": "bdb_read_misses",
            "write_hits": "bdb_write_hits",
            "write_misses": "bdb_write_misses",
            "total_keys": "bdb_no_of_keys",
            "expired_keys": "bdb_expired_objects",
            "evicted_keys": "bdb_evicted_objects",
        }

        metrics_to_query = metrics or list(default_metrics.keys())

        results = {
            "success": True,
            "cluster": cluster_fqdn,
            "time_range": time_range,
            "databases": {}
        }

        # Build all queries for batch execution
        batch_queries = {}
        for metric_name in metrics_to_query:
            if metric_name not in default_metrics:
                continue

            metric_expr = default_metrics[metric_name]

            # Build query - handle rate() expressions differently
            if metric_expr.startswith("rate("):
                query = metric_expr.replace("}", f', cluster="{cluster_fqdn}"}}')
            else:
                query = f'{metric_expr}{{cluster="{cluster_fqdn}"}}'

            batch_queries[metric_name] = query

        # Execute all queries in a single API call
        batch_result = self.query_prometheus_batch(
            batch_queries,
            start=f"now-{time_range}",
            end="now"
        )

        if not batch_result.get("success"):
            results["success"] = False
            results["error"] = batch_result.get("error")
            return results

        # Parse results for each metric
        all_results = batch_result.get("data", {}).get("results", {})

        for metric_name in metrics_to_query:
            if metric_name not in all_results:
                continue

            frames = all_results[metric_name].get("frames", [])

            for frame in frames:
                fields = frame.get("schema", {}).get("fields", [])
                data_values = frame.get("data", {}).get("values", [])

                if len(fields) > 1 and len(data_values) > 1:
                    labels = fields[1].get("labels", {})
                    bdb_id = labels.get("bdb", "unknown")
                    bdb_name = labels.get("bdb_name", "")

                    # Initialize database entry if needed
                    if bdb_id not in results["databases"]:
                        results["databases"][bdb_id] = {
                            "bdb_id": bdb_id,
                            "bdb_name": bdb_name,
                            "metrics": {}
                        }

                    # Get the latest value
                    if len(data_values[1]) > 0:
                        latest_value = data_values[1][-1]
                        results["databases"][bdb_id]["metrics"][metric_name] = latest_value

        # Add formatted metrics for convenience
        for bdb_id, db_data in results["databases"].items():
            metrics_data = db_data["metrics"]
            db_data["formatted"] = self._format_cluster_metrics(metrics_data)

        return results

    def _format_cluster_metrics(self, metrics: Dict[str, float]) -> Dict[str, str]:
        """Format raw metrics into human-readable strings."""
        formatted = {}

        formatters = {
            "connections": lambda v: f"{v:,.0f}",
            "ops_per_sec": lambda v: f"{v:,.0f} ops/s",
            "used_memory_bytes": lambda v: f"{v / (1024**3):.2f} GB",
            "avg_latency_sec": lambda v: f"{v * 1000:.3f} ms",
            "egress_bytes_per_sec": lambda v: f"{v / (1024**2):.2f} MB/s",
            "ingress_bytes_per_sec": lambda v: f"{v / (1024**2):.2f} MB/s",
            "read_hits": lambda v: f"{v:,.0f}",
            "read_misses": lambda v: f"{v:,.0f}",
            "write_hits": lambda v: f"{v:,.0f}",
            "write_misses": lambda v: f"{v:,.0f}",
            "total_keys": lambda v: f"{v:,.0f}",
            "expired_keys": lambda v: f"{v:,.0f}",
            "evicted_keys": lambda v: f"{v:,.0f}",
        }

        for metric_name, value in metrics.items():
            if value is not None and metric_name in formatters:
                try:
                    formatted[metric_name] = formatters[metric_name](value)
                except (TypeError, ValueError):
                    formatted[metric_name] = str(value)

        # Calculate hit ratios if we have the data
        read_hits = metrics.get("read_hits", 0)
        read_misses = metrics.get("read_misses", 0)
        if read_hits + read_misses > 0:
            hit_ratio = read_hits / (read_hits + read_misses) * 100
            formatted["read_hit_ratio"] = f"{hit_ratio:.1f}%"

        write_hits = metrics.get("write_hits", 0)
        write_misses = metrics.get("write_misses", 0)
        if write_hits + write_misses > 0:
            hit_ratio = write_hits / (write_hits + write_misses) * 100
            formatted["write_hit_ratio"] = f"{hit_ratio:.1f}%"

        return formatted

