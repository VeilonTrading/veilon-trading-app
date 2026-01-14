import os
from pathlib import Path

from dotenv import load_dotenv

# -------------------------------------------------------------------
# Locate and load .env at project root: veilon/.env
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../veilon
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# -------------------------------------------------------------------
# DATABASE CONFIG (required)
# -------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_required_db = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

_missing_db = [k for k, v in _required_db.items() if not v]
if _missing_db:
    raise RuntimeError(
        f"Missing required DB environment variables: {', '.join(_missing_db)}. "
        "Check your .env file."
    )


# -------------------------------------------------------------------
# AUTH / GOOGLE OAUTH CONFIG (optional here)
# -------------------------------------------------------------------
AUTH_REDIRECT_URI = os.getenv("AUTH_REDIRECT_URI")
AUTH_COOKIE_SECRET = os.getenv("AUTH_COOKIE_SECRET")
AUTH_CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = os.getenv("AUTH_CLIENT_SECRET")
AUTH_SERVER_METADATA_URL = os.getenv("AUTH_SERVER_METADATA_URL")

AUTH_CONFIG = {
    "redirect_uri": AUTH_REDIRECT_URI,
    "cookie_secret": AUTH_COOKIE_SECRET,
    "client_id": AUTH_CLIENT_ID,
    "client_secret": AUTH_CLIENT_SECRET,
    "server_metadata_url": AUTH_SERVER_METADATA_URL,
}

# NOTE: no hard failure here. Your auth layer should validate AUTH_CONFIG
# and raise with a clean error if anything critical is missing.


# -------------------------------------------------------------------
# OPTIONAL: MetaAPI Token
# -------------------------------------------------------------------
METAAPI_TOKEN = os.getenv("METAAPI_TOKEN")

if METAAPI_TOKEN is None:
    print("[WARN] METAAPI_TOKEN not found. Risk/Equity streaming may not work")