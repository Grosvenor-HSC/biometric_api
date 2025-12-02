# config.py — generated placeholder
import os
from dotenv import load_dotenv

load_dotenv()

SQL_CONN = os.getenv("BIOMETRIC_SQL_CONN", "")
if not SQL_CONN:
    raise RuntimeError("Missing BIOMETRIC_SQL_CONN in .env")

MAX_IMG_BYTES = int(os.getenv("MAX_IMG_BYTES", "1500000"))
HMAC_SECRET = os.getenv("HMAC_SHARED_SECRET", "")
API_TOKENS = set(filter(None, (os.getenv("BIOMETRIC_API_TOKENS") or "").replace(",", "\n").splitlines()))
TEMPLATE_DELETE_ENABLED = os.getenv("TEMPLATE_DELETE_ENABLED", "0").lower() in ("1", "true", "yes")
