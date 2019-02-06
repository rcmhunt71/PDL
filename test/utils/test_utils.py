import os
import uuid


def get_truncated_uuid() -> str:
    return str(uuid.uuid4()).split('-')[-1]


def get_pid() -> int:
    return os.getpid()
