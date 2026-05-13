# Claude Instructions for Redis Boilerplate Projects

This file provides instructions for AI assistants (Claude/Augment) working on projects
derived from this boilerplate. Read this file when starting work on any project that
uses this codebase as a foundation.

## Overview

This is a Redis Cloud operations boilerplate with pre-configured connectors for various
internal services. It is designed to accelerate development of tools and automation
for Redis Cloud operations, support, and engineering.

## 🔴 IMPORTANT: Use Glean for Redis Context

**When working on projects derived from this boilerplate, you have access to Redis's
internal knowledge base through Glean.** Use it proactively to gather context about:

- Redis Cloud architecture and features
- Internal processes and runbooks
- Customer-specific information
- Troubleshooting procedures
- Historical incidents and resolutions

### How to Use RedisKnowledge

```python
from connectors import RedisKnowledge

kb = RedisKnowledge()

# Ask any Redis-related question
result = kb.ask("How does Active-Active replication handle conflicts?")
print(result["answer"])

# Get troubleshooting help
result = kb.troubleshoot("customer seeing high latency on their cluster")

# Explain a concept
result = kb.explain_concept("RediSearch indexing")

# Find runbooks
result = kb.get_runbook("cluster failover procedure")

# Get customer context
result = kb.customer_context("Acme Corp", issue="connection timeouts")
```

### When to Use Glean

**ALWAYS query Glean when:**
1. You need to understand Redis Cloud architecture or features
2. You're troubleshooting an issue and need internal context
3. You need to find runbooks or operational procedures
4. You're working with customer-specific information
5. You need to understand internal processes or policies
6. You're unsure about Redis-specific terminology or concepts

**Before making assumptions about Redis internals, ASK GLEAN FIRST.**

## Available Connectors

This boilerplate provides the following pre-configured service connectors:

| Connector | Purpose | Usage |
|-----------|---------|-------|
| `RedisKnowledge` | **Redis context via Glean** | `kb.ask()`, `kb.troubleshoot()` |
| `GleanClient` | Raw Glean API access | `client.chat()`, `client.search()` |
| `GrafanaClient` | Metrics and dashboards | `client.query_prometheus()` |
| `SMDBClient` | Subscription/cluster data | `client.execute_query()` |
| `CloudExporterClient` | Cloud infrastructure data | `client.get_data()` |
| `JiraClient` | Issue tracking | `client.search_issues()`, `client.create_issue()` |
| `SquadcastClient` | Incident management | `client.get_incidents()` |
| `FirehydrantClient` | Incident management | `client.get_incidents()` |
| `AWSClient` | AWS resources | `client.get_caller_identity()` |
| `GCPClient` | GCP resources | `client.list_instances()` |
| `WildMooseClient` | AI debugging playbooks | `client.run_playbook()` |

## Project Structure

```
├── CLAUDE.md           # This file - AI assistant instructions
├── config/
│   ├── .env            # Environment variables (secrets - not in git)
│   ├── .env.example    # Template for environment variables
│   ├── settings.py     # Configuration classes
│   └── __init__.py
├── connectors/
│   ├── redis_knowledge.py  # Redis knowledge base (USE THIS!)
│   ├── glean_client.py     # Glean API client
│   ├── grafana_client.py   # Grafana/Prometheus client
│   ├── smdb_client.py      # SMDB MySQL client
│   ├── jira_client.py      # Jira API client
│   └── ...                 # Other service clients
├── main.py             # Connectivity test script
└── requirements.txt    # Python dependencies
```

## Development Patterns

### 1. Always Check Configuration First

```python
from connectors import RedisKnowledge

if RedisKnowledge.is_configured():
    kb = RedisKnowledge()
    # Use it
else:
    print("Glean not configured - check config/.env")
```

### 2. Handle Errors Gracefully

All connectors return dicts with a `success` key:

```python
result = kb.ask("my question")
if result["success"]:
    print(result["answer"])
else:
    print(f"Error: {result['error']}")
```

### 3. Use Sources for Verification

When Glean provides sources, include them for verification:

```python
result = kb.ask("question", include_sources=True)
for source in result.get("sources", []):
    print(f"  - {source['title']}: {source['url']}")
```

## Common Tasks

### Investigating a Customer Issue

```python
from connectors import RedisKnowledge, SMDBClient, JiraClient

kb = RedisKnowledge()
smdb = SMDBClient()
jira = JiraClient()

# 1. Get customer context from Glean
context = kb.customer_context("Customer Name", issue="the issue")

# 2. Query SMDB for cluster details
cluster_info = smdb.execute_query("SELECT * FROM clusters WHERE customer = %s", [customer_id])

# 3. Check for related Jira tickets
tickets = jira.search_issues(f'project = SUPPORT AND text ~ "Customer Name"')

# 4. Get troubleshooting guidance
guidance = kb.troubleshoot("specific issue description")
```

### Finding Documentation

```python
kb = RedisKnowledge()

# Search for docs
docs = kb.search_docs("Active-Active conflict resolution")

# Or ask directly
answer = kb.ask("How do I configure CRDB for multi-region?")
```

## Environment Setup

1. Copy `config/.env.example` to `config/.env`
2. Fill in the required credentials
3. For SMDB access, ensure SSH tunnel is running:
   ```bash
   ssh -L 3306:smdb.redislabs.com:3306 bastion
   ```

## Remember

- **Glean is your primary source for Redis-specific knowledge**
- Query it early and often when working on Redis-related tasks
- Include sources in your responses when available
- This boilerplate is designed to make Redis Cloud operations easier

