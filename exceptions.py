class ServerNotAvailableException(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f'Не удалось выполнить запрос - {self.status}'
