from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_cluster: str
    mongo_options: str
    mongo_username: str
    mongo_password: str
    mongo_db: str = "retrodex"
    
    @property
    def mongo_url(self) -> str:
        return(
            f"mongodb+srv://{self.mongo_username}:{self.mongo_password}"
            f"@{self.mongo_cluster}/?{self.mongo_options}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
