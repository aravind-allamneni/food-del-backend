from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_username: str
    db_password: str
    db_name: str
    secret_key: str
    algorithm: str
    access_token_expire_mins: int
    upload_folder: str

    class Config:
        env_file = ".env"


settings = Settings()
