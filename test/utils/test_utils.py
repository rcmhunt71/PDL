import uuid


def get_truncated_uuid():
    return str(uuid.uuid4()).split('-')[-1]
