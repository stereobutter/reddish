import socket
from reddish.clients._client_stubs import SyncRedis

class Redis(SyncRedis):
    def __init__(self, stream: socket.socket) -> None: ...
