import os
from pyutils.clogger.clogger import Clogger
from dotenv import load_dotenv

try:
    load_dotenv()
    Clogger.info("dotenv loaded successfully")
except ImportError:
    Clogger.error("dotenv threw an ImportError")
except Exception as e:
    Clogger.warning("dotenv was not loaded for some other reason")

def get_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        Clogger.error(f"ENV {name} NOT SET!!")
    return value
