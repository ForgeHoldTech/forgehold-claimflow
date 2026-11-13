import os

from pymongo import MongoClient

_client = None


def get_db():
    global _client
    if _client is None:
        _client = MongoClient(os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27018"))
    return _client[os.environ.get("MONGO_DB", "claimflow_logs")]