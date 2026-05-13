#!/usr/bin/env python3
"""
Boilerplate Project - Service Connectivity Checker

This script tests connectivity to all configured services and reports their status.
Use this as a template for building projects that integrate with these services.

Usage:
    1. Copy .env.example to .env
    2. Fill in your credentials in .env
    3. Run: python main.py
"""

import sys
from datetime import datetime

from config import validate_all_config
from connectors import (
    GrafanaClient,
    GleanClient,
    SMDBClient,
    CloudExporterClient,
    SquadcastClient,
    FirehydrantClient,
    AWSClient,
    GCPClient,
    WildMooseClient,
    JiraClient,
)


def print_header():
    """Print script header."""
    print("=" * 60)
    print("  Service Connectivity Checker")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def print_config_status():
    """Print configuration validation status."""
    print("Configuration Status:")
    print("-" * 40)

    config_status = validate_all_config()
    all_valid = True

    for service, status in config_status.items():
        if status['valid']:
            print(f"  ✓ {service}: configured")
        else:
            print(f"  ✗ {service}: missing {', '.join(status['missing'])}")
            all_valid = False

    print()
    return all_valid, config_status


def test_service(name: str, client_class, config_valid: bool) -> dict:
    """Test a single service connection."""
    if not config_valid:
        return {"tested": False, "reason": "not configured"}

    try:
        client = client_class()
        result = client.test_connection()
        return {"tested": True, "result": result}
    except Exception as e:
        return {"tested": True, "result": {"success": False, "error": str(e)}}


def test_all_services(config_status: dict):
    """Test connectivity to all services."""
    print("Connectivity Tests:")
    print("-" * 40)

    services = [
        ("grafana", "Grafana/Prometheus", GrafanaClient),
        ("glean", "Glean AI", GleanClient),
        ("smdb", "SMDB (MySQL)", SMDBClient),
        ("cloud_exporter", "Cloud Exporter", CloudExporterClient),
        ("squadcast", "Squadcast", SquadcastClient),
        ("firehydrant", "Firehydrant", FirehydrantClient),
        ("aws", "AWS", AWSClient),
        ("gcp", "GCP", GCPClient),
        ("wildmoose", "WildMoose", WildMooseClient),
        ("jira", "Jira", JiraClient),
    ]

    results = {}
    for config_key, display_name, client_class in services:
        config_valid = config_status.get(config_key, {}).get('valid', False)
        result = test_service(config_key, client_class, config_valid)
        results[config_key] = result

        if not result["tested"]:
            print(f"  ⊘ {display_name}: skipped ({result['reason']})")
        elif result["result"]["success"]:
            status = result["result"].get("status", "connected")
            print(f"  ✓ {display_name}: connected")
        else:
            error = result["result"].get("error", "unknown error")
            print(f"  ✗ {display_name}: {error[:50]}...")

    print()
    return results


def print_summary(results: dict):
    """Print summary of test results."""
    print("Summary:")
    print("-" * 40)

    tested = sum(1 for r in results.values() if r["tested"])
    passed = sum(1 for r in results.values() if r["tested"] and r["result"]["success"])
    failed = tested - passed
    skipped = len(results) - tested

    print(f"  Total services: {len(results)}")
    print(f"  Tested: {tested}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print()

    if failed > 0:
        print("Failed services:")
        for name, result in results.items():
            if result["tested"] and not result["result"]["success"]:
                print(f"  - {name}: {result['result'].get('error', 'unknown')}")
        print()


def main():
    """Main entry point."""
    print_header()

    # Validate configuration
    all_valid, config_status = print_config_status()

    if not any(s['valid'] for s in config_status.values()):
        print("No services are configured. Please set up your .env file.")
        print("See .env.example for required environment variables.")
        sys.exit(1)

    # Test connectivity
    results = test_all_services(config_status)

    # Print summary
    print_summary(results)

    # Exit with error code if any tests failed
    failed = sum(1 for r in results.values() if r["tested"] and not r["result"]["success"])
    sys.exit(1 if failed > 0 else 0)


if __name__ == '__main__':
    main()
