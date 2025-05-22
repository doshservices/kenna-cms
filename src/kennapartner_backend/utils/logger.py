import logging
import os

log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

app_log_path = os.path.join(log_dir, "app.log")
error_log_path = os.path.join(log_dir, "error.log")

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

app_handler = logging.FileHandler(app_log_path)
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(formatter)


error_handler = logging.FileHandler(app_log_path)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)