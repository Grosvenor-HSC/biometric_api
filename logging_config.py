# logging_config.py — generated placeholder
import os, logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler("logs/biometric_api.log", maxBytes=10_000_000, backupCount=5)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)
    log = logging.getLogger("biometric_api")
    log.info("Logging initialized.")
    return log
