class RequestException(Exception):
    msg: str
    status: int
    response: dict

    def __init__(self, msg: str, status: int, response: dict, *args, **kwargs):
        self.msg = msg
        self.status = status
        self.response = response

    def __str__(self):
        return f"{self.msg}\n -статус: {self.status}\n {self.response}"


class TooManyRetries(Exception):
    def __str__(self):
        return "Превышено количество допустимых попыток запроса"
