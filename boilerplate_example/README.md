# Redis Cloud Operations Boilerplate

A unified Python boilerplate with pre-configured connectors for Redis Cloud operations, support, and engineering tools. Stop reinventing the wheel—start building solutions.

## 🚀 Quick Start

```bash
# 1. Clone/copy the boilerplate
cp -r boilerplate_example my_new_tool
cd my_new_tool

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials (already set up if using shared .env)
cp config/.env.example config/.env
# Edit config/.env with your credentials

# 5. Test connectivity
python main.py
```

## 📦 Available Connectors

| Connector | Purpose | Key Methods |
|-----------|---------|-------------|
| `GrafanaClient` | Prometheus metrics, cluster dashboards | `query_prometheus()`, `get_cluster_metrics()` |
| `RedisKnowledge` | AI-powered Redis knowledge base (Glean) | `ask()`, `troubleshoot()`, `get_runbook()` |
| `GleanClient` | Raw Glean API access | `chat()`, `search()` |
| `SMDBClient` | Subscription/cluster database queries | `execute_query()` |
| `JiraClient` | Issue tracking and management | `search_issues()`, `create_issue()`, `get_issue()` |
| `SquadcastClient` | Incident management | `get_incidents()`, `get_open_incidents()` |
| `FirehydrantClient` | Incident response | `get_incidents()`, `get_services()` |
| `AWSClient` | AWS infrastructure access | `get_caller_identity()`, `get_client()` |
| `GCPClient` | GCP infrastructure access | `list_instances()`, `get_project()` |
| `WildMooseClient` | AI debugging playbooks | `run_playbook()`, `list_playbooks()` |
| `CloudExporterClient` | Cloud infrastructure metrics | `get_data()` |

## 💡 Usage Examples

### Get Cluster Metrics
```python
from connectors import GrafanaClient

client = GrafanaClient()
result = client.get_cluster_metrics("c42998.us-east-1-mz.ec2.cloud.rlrcp.com")

for bdb_id, db in result["databases"].items():
    print(f"{db['bdb_name']}: {db['formatted']['connections']} connections")
```

### AI-Powered Troubleshooting
```python
from connectors import RedisKnowledge

kb = RedisKnowledge()
result = kb.troubleshoot("customer seeing high latency on cluster")
print(result["answer"])
```

### Query SMDB
```python
from connectors import SMDBClient

smdb = SMDBClient()
result = smdb.execute_query(
    "SELECT * FROM clusters WHERE cluster_fqdn = %s",
    ["c42998.us-east-1-mz.ec2.cloud.rlrcp.com"]
)
```

### Search Jira Issues
```python
from connectors import JiraClient

jira = JiraClient()
result = jira.search_issues('project = RED AND status = Open ORDER BY created DESC')
for issue in result["issues"]:
    print(f"{issue['key']}: {issue['fields']['summary']}")
```

### Get Today's Incidents
```python
from connectors import SquadcastClient

client = SquadcastClient()
result = client.get_incidents(limit=50)
incidents = result["incidents"]["incidents"]  # Note: nested structure
```

## 📁 Project Structure

```
├── config/
│   ├── .env              # Your credentials (gitignored)
│   ├── .env.example      # Template for credentials
│   ├── settings.py       # Configuration classes
│   └── __init__.py
├── connectors/
│   ├── grafana_client.py
│   ├── redis_knowledge.py
│   ├── glean_client.py
│   ├── smdb_client.py
│   ├── jira_client.py
│   ├── squadcast_client.py
│   ├── firehydrant_client.py
│   ├── aws_client.py
│   ├── gcp_client.py
│   ├── wildmoose_client.py
│   ├── cloud_exporter_client.py
│   └── __init__.py
├── certs/                # SSL certificates (gitignored)
├── main.py               # Connectivity test script
├── requirements.txt
├── CLAUDE.md             # AI assistant instructions
└── README.md
```

## 🔧 Configuration

All credentials are stored in `config/.env`. See `config/.env.example` for the full list of required variables.

### Required for Each Service

| Service | Required Variables |
|---------|-------------------|
| Grafana | `GRAFANA_URL`, `GRAFANA_API_TOKEN`, `PROM_DATASOURCE_UID` |
| Glean | `GLEAN_BASE_URL`, `GLEAN_API_TOKEN` |
| SMDB | `SMDB_HOST`, `SMDB_PORT`, `SMDB_USER`, `SMDB_PASSWORD`, `SMDB_DATABASE`, certs |
| Jira | `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN` |
| Squadcast | `SQUADCAST_BEARER_TOKEN`, API URLs |
| Firehydrant | `FIREHYDRANT_API_TOKEN`, `FIREHYDRANT_BASE_URL` |
| AWS | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| GCP | `GOOGLE_APPLICATION_CREDENTIALS` or individual creds |
| WildMoose | `WILDMOOSE_BASE_URL`, `WILDMOOSE_API_TOKEN` |

### SMDB SSH Tunnel

SMDB requires an SSH tunnel to be running:
```bash
ssh -L 3306:smdb.redislabs.com:3306 bastion
```

## 🧪 Testing Connectivity

Run the connectivity checker to verify all services:

```bash
python main.py
```

Example output:
```
============================================================
  Service Connectivity Checker
  Run at: 2026-02-03 17:45:00
============================================================

Configuration Status:
----------------------------------------
  ✓ grafana: configured
  ✓ glean: configured
  ✓ jira: configured
  ...

Connectivity Tests:
----------------------------------------
  ✓ Grafana/Prometheus: connected
  ✓ Glean AI: connected
  ✓ Jira: connected
  ...
```

## 🤖 AI Assistant Integration

This boilerplate includes `CLAUDE.md` with instructions for AI assistants. When using Claude/Augment on projects derived from this boilerplate:

1. **RedisKnowledge is your friend** - Use it to query internal docs, runbooks, and troubleshooting guides
2. **All connectors follow the same pattern** - Check `is_configured()`, create client, call methods
3. **Results include success flag** - Always check `result["success"]` before accessing data

## 📊 Building Tools

### Customer Investigation Tool
```python
from connectors import RedisKnowledge, SMDBClient, JiraClient, GrafanaClient

# Gather all context for a customer issue
kb = RedisKnowledge()
smdb = SMDBClient()
jira = JiraClient()
grafana = GrafanaClient()

# 1. Get AI-powered context
context = kb.customer_context("Acme Corp", issue="high latency")

# 2. Query cluster data
cluster = smdb.execute_query("SELECT * FROM clusters WHERE customer = %s", [customer_id])

# 3. Get metrics
metrics = grafana.get_cluster_metrics(cluster_fqdn)

# 4. Find related tickets
tickets = jira.search_issues(f'text ~ "Acme Corp" ORDER BY created DESC')
```

### Incident Response Dashboard
```python
from connectors import SquadcastClient, GrafanaClient, RedisKnowledge

squadcast = SquadcastClient()
grafana = GrafanaClient()
kb = RedisKnowledge()

# Get open incidents
incidents = squadcast.get_open_incidents()

for incident in incidents:
    cluster = incident.get("tags", {}).get("Cluster", {}).get("value")
    if cluster:
        # Get cluster metrics
        metrics = grafana.get_cluster_metrics(cluster)
        # Get troubleshooting guidance
        guidance = kb.troubleshoot(incident.get("message", ""))
```

## 📝 License

Internal Redis use only.

## 🙋 Support

For issues with this boilerplate, contact the Cloud Operations team.
