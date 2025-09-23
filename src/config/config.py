from dotenv import load_dotenv, dotenv_values

load_dotenv()

env_config = dotenv_values(".env")

is_dev = env_config["MODE"] == "development"
db_url = (
    f"postgresql+asyncpg://{env_config['DB_USER']}:{env_config['DB_PASS']}"
    f"@{env_config['DB_HOST']}:{env_config['DB_PORT']}/{env_config['DB_NAME']}"
)
jwt_secret_key = env_config["JWT_TOKEN"]
jwt_access_expires_in = env_config["JWT_ACCESS_EXPIRES_IN"]
jwt_refresh_expires_in = env_config["JWT_REFRESH_EXPIRES_IN"]
