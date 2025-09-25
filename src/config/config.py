from dotenv import load_dotenv, dotenv_values

load_dotenv()

env_config = dotenv_values(".env")

# mode
is_dev = env_config["MODE"] == "development"

# db
db_url = (
    f"postgresql+asyncpg://{env_config['DB_USER']}:{env_config['DB_PASS']}"
    f"@{env_config['DB_HOST']}:{env_config['DB_PORT']}/{env_config['DB_NAME']}"
)

# jwt
jwt_secret_key = env_config["JWT_TOKEN"]
jwt_access_expires_in = env_config["JWT_ACCESS_EXPIRES_IN"]
jwt_refresh_expires_in = env_config["JWT_REFRESH_EXPIRES_IN"]

# storage
storage_host = env_config["STORAGE_HOST"]
storage_port = env_config["STORAGE_PORT"]
storage_access_key = env_config["STORAGE_ACCESS_KEY"]
storage_secret_key = env_config["STORAGE_SECRET_KEY"]
