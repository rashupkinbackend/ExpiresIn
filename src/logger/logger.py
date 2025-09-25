import logging
from src.config.config import is_dev

level = logging.DEBUG if is_dev else logging.INFO

logging.basicConfig(
    level=level,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
