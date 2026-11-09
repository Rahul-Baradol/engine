import os
from core.enums import LogType

ENABLE_LOGS = os.getenv("ENABLE_LOGS", 0)

def server_log(log_type: LogType, message: str, force_log: bool = False):
    if ENABLE_LOGS or force_log:
        print(f"{log_type.name}: {message}")