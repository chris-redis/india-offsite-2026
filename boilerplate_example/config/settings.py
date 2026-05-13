"""
Configuration settings for the boilerplate project.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (in config folder)
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class GrafanaConfig:
    """Grafana/Prometheus configuration."""
    URL = os.getenv("GRAFANA_URL", "https://monitoringcloud.redislabs.com/grafana")
    API_TOKEN = os.getenv("GRAFANA_API_TOKEN")
    PROM_DATASOURCE_UID = os.getenv("PROM_DATASOURCE_UID", "P9E3C2526B28249DF")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration. Returns True if valid."""
        return cls.API_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        """Return list of missing required config items."""
        missing = []
        if not cls.API_TOKEN:
            missing.append("GRAFANA_API_TOKEN")
        return missing


class GleanConfig:
    """Glean AI configuration."""
    BASE_URL = os.getenv("GLEAN_BASE_URL", "https://redis-be.glean.com/")
    API_TOKEN = os.getenv("GLEAN_API_TOKEN")

    @classmethod
    def validate(cls) -> bool:
        return cls.API_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.API_TOKEN:
            missing.append("GLEAN_API_TOKEN")
        return missing


class SMDBConfig:
    """SMDB (MySQL) database configuration."""
    HOST = os.getenv("SMDB_HOST", "127.0.0.1")
    PORT = int(os.getenv("SMDB_PORT", "3306"))
    USER = os.getenv("SMDB_USER", "devops.readonly")
    PASSWORD = os.getenv("SMDB_PASSWORD")
    DATABASE = os.getenv("SMDB_DATABASE", "garantiaSM")
    CERT_FILE = os.getenv("SMDB_CERT_FILE")
    KEY_FILE = os.getenv("SMDB_KEY_FILE")

    @classmethod
    def validate(cls) -> bool:
        return cls.PASSWORD is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.PASSWORD:
            missing.append("SMDB_PASSWORD")
        return missing


class CloudExporterConfig:
    """Cloud Exporter API configuration."""
    URL = os.getenv("CLOUD_EXPORTER_URL",
                    "https://api.cloud-cluster-exporter.redislabs.com/json?data_type=cluster_info")
    CERT_FILE = os.getenv("CLOUD_EXPORTER_CERT_FILE")
    KEY_FILE = os.getenv("CLOUD_EXPORTER_KEY_FILE")

    @classmethod
    def validate(cls) -> bool:
        return cls.CERT_FILE is not None and cls.KEY_FILE is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.CERT_FILE:
            missing.append("CLOUD_EXPORTER_CERT_FILE")
        if not cls.KEY_FILE:
            missing.append("CLOUD_EXPORTER_KEY_FILE")
        return missing


class SquadcastConfig:
    """Squadcast configuration."""
    BEARER_TOKEN = os.getenv("SQUADCAST_BEARER_TOKEN")
    AUTH_URL = os.getenv("SQUADCAST_AUTH", "https://auth.eu.squadcast.com/oauth/access-token")
    URL_TEAMS = os.getenv("SQUADCAST_URL_TEAMS", "https://api.eu.squadcast.com/v3/teams")
    URL_SERVICES = os.getenv("SQUADCAST_URL_SERVICES", "https://api.eu.squadcast.com/v3/services")
    URL_INCIDENTS = os.getenv("SQUADCAST_URL_INCIDENTS", "https://api.eu.squadcast.com/v3/incidents")

    @classmethod
    def validate(cls) -> bool:
        return cls.BEARER_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.BEARER_TOKEN:
            missing.append("SQUADCAST_BEARER_TOKEN")
        return missing


class FirehydrantConfig:
    """Firehydrant configuration."""
    API_TOKEN = os.getenv("FIREHYDRANT_API_TOKEN")
    BASE_URL = os.getenv("FIREHYDRANT_BASE_URL", "https://api.firehydrant.io/v1")

    @classmethod
    def validate(cls) -> bool:
        return cls.API_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.API_TOKEN:
            missing.append("FIREHYDRANT_API_TOKEN")
        return missing


class AWSConfig:
    """AWS configuration."""
    ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
    DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    @classmethod
    def validate(cls) -> bool:
        return cls.ACCESS_KEY_ID is not None and cls.SECRET_ACCESS_KEY is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.ACCESS_KEY_ID:
            missing.append("AWS_ACCESS_KEY_ID")
        if not cls.SECRET_ACCESS_KEY:
            missing.append("AWS_SECRET_ACCESS_KEY")
        return missing


class GCPConfig:
    """GCP configuration."""
    CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    CLIENT_EMAIL = os.getenv("GCP_CLIENT_EMAIL")
    PRIVATE_KEY = os.getenv("GCP_PRIVATE_KEY")

    @classmethod
    def validate(cls) -> bool:
        # Either credentials file OR individual credentials
        if cls.CREDENTIALS_FILE:
            return Path(cls.CREDENTIALS_FILE).exists()
        return cls.PROJECT_ID is not None and cls.CLIENT_EMAIL is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.CREDENTIALS_FILE and not cls.PROJECT_ID:
            missing.append("GOOGLE_APPLICATION_CREDENTIALS or GCP_PROJECT_ID")
        return missing


class WildMooseConfig:
    """WildMoose API configuration."""
    BASE_URL = os.getenv("WILDMOOSE_BASE_URL", "https://api.wildmoose.ai")
    API_TOKEN = os.getenv("WILDMOOSE_API_TOKEN")
    # Auth0 credentials for JWT token generation (if needed)
    AUTH0_CLIENT_ID = os.getenv("WILDMOOSE_AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("WILDMOOSE_AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN = os.getenv("WILDMOOSE_AUTH0_DOMAIN")

    @classmethod
    def validate(cls) -> bool:
        return cls.API_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.API_TOKEN:
            missing.append("WILDMOOSE_API_TOKEN")
        return missing


class JiraConfig:
    """Jira API configuration."""
    URL = os.getenv("JIRA_URL", "https://redislabs.atlassian.net")
    USER = os.getenv("JIRA_USER")
    API_TOKEN = os.getenv("JIRA_API_TOKEN")

    @classmethod
    def validate(cls) -> bool:
        return cls.USER is not None and cls.API_TOKEN is not None

    @classmethod
    def get_missing(cls) -> list:
        missing = []
        if not cls.USER:
            missing.append("JIRA_USER")
        if not cls.API_TOKEN:
            missing.append("JIRA_API_TOKEN")
        return missing


def validate_all_config() -> dict:
    """
    Validate all configuration settings.
    Returns dict with service names as keys and validation status.
    """
    configs = {
        'grafana': GrafanaConfig,
        'glean': GleanConfig,
        'smdb': SMDBConfig,
        'cloud_exporter': CloudExporterConfig,
        'squadcast': SquadcastConfig,
        'firehydrant': FirehydrantConfig,
        'aws': AWSConfig,
        'gcp': GCPConfig,
        'wildmoose': WildMooseConfig,
        'jira': JiraConfig,
    }

    results = {}
    for name, config_class in configs.items():
        results[name] = {
            'valid': config_class.validate(),
            'missing': config_class.get_missing()
        }

    return results

