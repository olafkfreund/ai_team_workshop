"""
Configuration management for MCP Server
Supports multiple environments and secure secret handling
"""
import os
from typing import Optional
from dataclasses import dataclass
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


@dataclass
class Config:
    """Application configuration"""
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = False
    WORKERS: int = 4
    
    # Azure settings
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: str = "copilot-resources"
    AZURE_KEY_VAULT_URL: Optional[str] = None
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Security settings
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = None
    
    # Features
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 300
    ENABLE_AUDIT_LOGGING: bool = True


class ConfigManager:
    """Manages configuration loading from multiple sources"""
    
    def __init__(self):
        self.config = Config()
        self._load_from_environment()
        self._load_from_key_vault()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Server settings
        self.config.HOST = os.getenv("MCP_HOST", self.config.HOST)
        self.config.PORT = int(os.getenv("MCP_PORT", self.config.PORT))
        self.config.DEBUG = os.getenv("MCP_DEBUG", "false").lower() == "true"
        self.config.WORKERS = int(os.getenv("MCP_WORKERS", self.config.WORKERS))
        
        # Azure settings
        self.config.AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.config.AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.config.AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", self.config.AZURE_STORAGE_CONTAINER_NAME)
        self.config.AZURE_KEY_VAULT_URL = os.getenv("AZURE_KEY_VAULT_URL")
        
        # Redis settings
        self.config.REDIS_HOST = os.getenv("REDIS_HOST", self.config.REDIS_HOST)
        self.config.REDIS_PORT = int(os.getenv("REDIS_PORT", self.config.REDIS_PORT))
        self.config.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        
        # Security
        self.config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        
        # Monitoring
        self.config.APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        
        # Features
        self.config.ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        self.config.ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
    
    def _load_from_key_vault(self):
        """Load secrets from Azure Key Vault if configured"""
        if not self.config.AZURE_KEY_VAULT_URL:
            return
        
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=self.config.AZURE_KEY_VAULT_URL, credential=credential)
            
            # Load JWT secret from Key Vault
            if not self.config.JWT_SECRET_KEY:
                try:
                    secret = client.get_secret("jwt-secret-key")
                    self.config.JWT_SECRET_KEY = secret.value
                except Exception:
                    pass  # Secret not found, will use environment or generate
            
            # Load storage connection string from Key Vault
            if not self.config.AZURE_STORAGE_CONNECTION_STRING:
                try:
                    secret = client.get_secret("storage-connection-string")
                    self.config.AZURE_STORAGE_CONNECTION_STRING = secret.value
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"Warning: Could not load secrets from Key Vault: {e}")
    
    def get_config(self) -> Config:
        """Get the current configuration"""
        return self.config


# Global configuration instance
config_manager = ConfigManager()
config = config_manager.get_config()
