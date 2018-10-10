import os
import uuid


def get_truncated_uuid():
    return str(uuid.uuid4()).split('-')[-1]


def get_pid():
    return os.getpid()
