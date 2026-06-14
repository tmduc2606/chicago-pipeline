from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "chicago"
    postgres_user: str = "chicago"
    postgres_password: str = "change_me_local"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "changeme"
    airflow_base_url: str = "http://localhost:8080"
    airflow_user: str = "admin"
    airflow_password: str = "admin"
    env: str = "local"
    cache_ttl: int = 300

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}"

    model_config = {"env_prefix": "API_"}


settings = Settings()
