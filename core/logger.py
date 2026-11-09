from core.env import ENABLE_LOGS
import os
from core.enums import LogType

def server_log(log_type: LogType, message: str, force_log: bool = False):
    if ENABLE_LOGS or force_log:
        print(f"{log_type.name}: {message}")