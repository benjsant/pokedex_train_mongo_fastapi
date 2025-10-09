from pydantic_settings import BaseSettings


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

    class Config: 
        env_file = ".env"

settings = Settings()
