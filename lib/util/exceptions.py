from typing import List

class IndexedException(Exception):
    def __init__(self, id: int, message: str):
        self.error_id = id
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f'code({self.error_id}) {self.message}'

class RegistrationError(IndexedException):
    pass

class EmailValidationError(RegistrationError):
    def __init__(self, id: int, message: str, link: str = None):
        self.link = link
        super().__init__(id, message)

class NotAutorizedError(IndexedException):
    def __init__(self):
        super().__init__(-1002, 'You are not authorized to execute this request.')

class NoPermissionError(IndexedException):
    def __init__(self):
        super().__init__(-1003, 'You don\'t have no permission to execute this request.')

class NoJsonError(IndexedException):
    def __init__(self):
        super().__init__(-1004, 'This request requires json to be send, but there was none or it was corrupted.')

class NotEnoughDataError(IndexedException):
    def __init__(self, sent: List[str], needed: List[str]):
        super().__init__(-1005, f'This request requires json to have next fields: {needed}, but got only: {sent}.')