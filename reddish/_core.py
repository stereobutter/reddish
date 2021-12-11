class Redis:

    def send(self, commands):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
