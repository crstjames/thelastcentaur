import os
import pytest
from src.core.config import Settings, settings

class TestSettings:
    def test_settings_values(self):
        """Test that settings are loaded correctly from environment variables."""
        # Set test environment variables
        os.environ["SECRET_KEY"] = "test_secret_key"
        os.environ["ALGORITHM"] = "HS512"
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
        os.environ["POSTGRES_SERVER"] = "test_server"
        os.environ["POSTGRES_USER"] = "test_user"
        os.environ["POSTGRES_PASSWORD"] = "test_password"
        os.environ["POSTGRES_DB"] = "test_db"
        
        # Create a new settings instance to pick up the environment variables
        test_settings = Settings()
        
        # Check that the values match the environment variables
        assert test_settings.SECRET_KEY == "test_secret_key"
        assert test_settings.ALGORITHM == "HS512"
        assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert test_settings.POSTGRES_SERVER == "test_server"
        assert test_settings.POSTGRES_USER == "test_user"
        assert test_settings.POSTGRES_PASSWORD == "test_password"
        assert test_settings.POSTGRES_DB == "test_db"
    
    def test_database_url_construction(self):
        """Test that the database URL is constructed correctly."""
        # Set test environment variables
        os.environ["POSTGRES_SERVER"] = "db_server"
        os.environ["POSTGRES_USER"] = "db_user"
        os.environ["POSTGRES_PASSWORD"] = "db_password"
        os.environ["POSTGRES_DB"] = "db_name"
        
        # Create a new settings instance
        test_settings = Settings()
        
        # Check the database URL
        expected_url = "postgresql+asyncpg://db_user:db_password@db_server/db_name"
        assert test_settings.SQLALCHEMY_DATABASE_URI == expected_url
    
    def test_settings_singleton(self):
        """Test that the settings object is a singleton."""
        # The imported settings should be the same object as a new Settings instance
        assert isinstance(settings, Settings)
        
        # Changing an environment variable and creating a new Settings instance
        # should not affect the singleton
        original_secret = settings.SECRET_KEY
        os.environ["SECRET_KEY"] = "new_secret_key"
        new_settings = Settings()
        
        # The singleton should have the original value
        assert settings.SECRET_KEY == original_secret
        # But the new instance should have the new value
        assert new_settings.SECRET_KEY == "new_secret_key" 