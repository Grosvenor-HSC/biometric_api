# biometric_api/auth.py

import base64
import hashlib
import hmac
import logging

from fastapi import Header, HTTPException, Request
from biometric_api.config import HMAC_SECRET, API_TOKENS  # reuse config

logger = logging.getLogger(__name__)

HMAC_SHARED_SECRET = HMAC_SECRET


async def require_signed_request(
    request: Request,
    x_api_token: str = Header(default=None, alias="X-Api-Token"),
    x_hmac_timestamp: str = Header(default=None, alias="X-HMAC-Timestamp"),
    x_hmac_signature: str = Header(default=None, alias="X-HMAC-Signature"),
):
    logger.info("Auth check starting...")
    logger.info("Token header      : %r", x_api_token)
    logger.info("Timestamp header  : %r", x_hmac_timestamp)
    logger.info("Signature header  : %r", x_hmac_signature)
    logger.info("Configured tokens : %r", API_TOKENS)

    # 1) Token check
    if not API_TOKENS:
        logger.error("No API_TOKENS configured on server.")
        raise HTTPException(status_code=500, detail="server misconfigured: no API tokens")

    if x_api_token not in API_TOKENS:
        logger.warning("Rejecting: invalid API token.")
        raise HTTPException(status_code=403, detail="invalid token")

    # 2) If no HMAC secret configured, accept token-only
    if not HMAC_SHARED_SECRET:
        logger.info("No HMAC_SHARED_SECRET configured, token-only auth accepted.")
        return True

    # 3) Basic header sanity
    if not x_hmac_timestamp or not x_hmac_signature:
        logger.warning("Rejecting: missing HMAC headers.")
        raise HTTPException(status_code=403, detail="missing hmac headers")

    # 4) Compute body hash EXACTLY as client does: sha256(raw body) -> hex lowercase
    body = await request.body()
    body_hash = hashlib.sha256(body).hexdigest()

    method = request.method.upper()
    path = request.url.path

    expected_message = f"{x_hmac_timestamp}\n{method}\n{path}\n{body_hash}"

    logger.info("Expected message for HMAC:\n%s", expected_message)
    logger.info("Request path  : %s", path)
    logger.info("Request method: %s", method)
    logger.info("Body hash     : %s", body_hash)

    # 5) Decode secret and compute expected signature
    try:
        key_bytes = base64.b64decode(HMAC_SHARED_SECRET)
    except Exception as e:
        logger.exception("Failed to base64-decode HMAC_SHARED_SECRET: %s", e)
        raise HTTPException(status_code=500, detail="server HMAC misconfiguration")

    digest = hmac.new(key_bytes, expected_message.encode("utf-8"), hashlib.sha256).digest()
    expected_sig = base64.b64encode(digest).decode("ascii")

    logger.info("Expected signature: %s", expected_sig)
    logger.info("Client signature  : %s", x_hmac_signature)

    if not hmac.compare_digest(expected_sig, x_hmac_signature):
        logger.warning("Rejecting: signature mismatch.")
        raise HTTPException(status_code=403, detail="bad signature")

    logger.info("HMAC verification succeeded.")
    return True
