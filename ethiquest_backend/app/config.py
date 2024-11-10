from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Basic App Config
    APP_NAME: str = "EthiQuest"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://ethiquest:ethiquest@localhost:5432/ethiquest"
    )
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Redis Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_TTL: int = 3600  # 1 hour default cache TTL
    
    # AI Service Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "anthropic")  # anthropic or openai
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = "claude-3-opus-20240229"  # or gpt-4 for OpenAI
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    
    # Game Settings
    STARTING_CAPITAL: int = 1_000_000
    STARTING_EMPLOYEES: int = 10
    INITIAL_REPUTATION: float = 50.0
    MIN_DECISIONS_FOR_ANALYSIS: int = 5
    
    # Difficulty Settings
    DIFFICULTY_LEVELS: dict = {
        "beginner": {
            "time_pressure": 0.5,
            "complexity": 0.3,
            "stakes": 0.2
        },
        "intermediate": {
            "time_pressure": 0.7,
            "complexity": 0.6,
            "stakes": 0.5
        },
        "advanced": {
            "time_pressure": 0.9,
            "complexity": 0.8,
            "stakes": 0.8
        }
    }
    
    # Stakeholder Categories
    STAKEHOLDER_TYPES: list = [
        "employees",
        "customers",
        "investors",
        "community",
        "environment"
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "ethiquest.log"
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Cache Settings
    SCENARIO_CACHE_TTL: int = 3600  # 1 hour
    PLAYER_CACHE_TTL: int = 86400  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        """Pydantic config class"""
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    def get_database_args(self) -> dict:
        """Get database connection arguments"""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT
        }
    
    def get_ai_config(self) -> dict:
        """Get AI service configuration"""
        return {
            "provider": self.AI_PROVIDER,
            "api_key": self.AI_API_KEY,
            "model": self.AI_MODEL,
            "temperature": self.AI_TEMPERATURE,
            "max_tokens": self.AI_MAX_TOKENS
        }
    
    def get_redis_config(self) -> dict:
        """Get Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "ttl": self.REDIS_TTL
        }
    
    def get_game_settings(self) -> dict:
        """Get game-specific settings"""
        return {
            "starting_capital": self.STARTING_CAPITAL,
            "starting_employees": self.STARTING_EMPLOYEES,
            "initial_reputation": self.INITIAL_REPUTATION,
            "min_decisions": self.MIN_DECISIONS_FOR_ANALYSIS,
            "difficulty_levels": self.DIFFICULTY_LEVELS,
            "stakeholder_types": self.STAKEHOLDER_TYPES
        }

@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance"""
    return Settings()

# Example environment variables file (.env)
ENV_EXAMPLE = """
# Application Settings
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://ethiquest:ethiquest@localhost:5432/ethiquest

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Service
AI_PROVIDER=anthropic
AI_API_KEY=your-api-key-here

# Logging
LOG_LEVEL=INFO
"""

def create_env_example():
    """Create example .env file"""
    with open(".env.example", "w") as f:
        f.write(ENV_EXAMPLE)

def validate_environment():
    """Validate required environment variables"""
    settings = get_settings()
    
    # Check critical settings
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-here":
        raise ValueError("SECRET_KEY must be set in production")
    
    if not settings.AI_API_KEY:
        raise ValueError("AI_API_KEY must be set")
    
    # Create upload directory if it doesn't exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    return True

if __name__ == "__main__":
    # Create example environment file
    create_env_example()
    
    # Validate environment
    try:
        validate_environment()
        print("Environment configuration is valid.")
    except ValueError as e:
        print(f"Environment configuration error: {e}")
