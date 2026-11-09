import os
from dotenv import load_dotenv

load_dotenv()

SERVER_BIND_ADDRESS = os.getenv("SERVER_BIND_ADDRESS", "0.0.0.0")
SERVER_BIND_PORT = int(os.getenv("SERVER_BIND_PORT", 8080))
ENABLE_LOGS = int(os.getenv("ENABLE_LOGS", 0))