from typing import Any, Dict, Optional, List, Tuple
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "The Last Centaur"
    
    # Security
    SECRET_KEY: str = "testsecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "thelastcentaur"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Game Settings
    MAX_CONCURRENT_GAMES: int = 1000
    GAME_MAP_SIZE_X: int = 10
    GAME_MAP_SIZE_Y: int = 10
    GAME_TICK_RATE: float = 0.1  # seconds
    
    # Environment
    ENVIRONMENT: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields
    )
    
    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    def parse_token_expire_minutes(cls, v: Any) -> int:
        """Parse ACCESS_TOKEN_EXPIRE_MINUTES to handle potential comments or whitespace."""
        if isinstance(v, str):
            # Extract only the numeric part if there are comments
            import re
            if match := re.match(r'^\s*(\d+)', v):
                return int(match.group(1))
        return v
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        return f"postgresql+asyncpg://{values.data.get('POSTGRES_USER')}:{values.data.get('POSTGRES_PASSWORD')}@{values.data.get('POSTGRES_SERVER')}/{values.data.get('POSTGRES_DB')}"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def game_map_size(self) -> Tuple[int, int]:
        """Get the game map size as a tuple."""
        return (self.GAME_MAP_SIZE_X, self.GAME_MAP_SIZE_Y)

# Create global settings instance
settings = Settings() 