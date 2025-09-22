from dotenv import load_dotenv, dotenv_values

load_dotenv()

env_config = dotenv_values('.env')

db_url = (f"postgresql+asyncpg://{env_config['DB_USER']}:{env_config['DB_PASS']}"
          f"@{env_config['DB_HOST']}:{env_config['DB_PORT']}/{env_config['DB_NAME']}"
)
