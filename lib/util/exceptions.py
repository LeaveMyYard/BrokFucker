from typing import List

class IndexedException(Exception):
    '''
        REST API Indexed Exception
    '''
    def __init__(self, id: int, message: str):
        self.error_id = id
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f'code({self.error_id}) {self.message}'

class RegistrationError(IndexedException):
    pass

class EmailValidationError(RegistrationError):
    pass

class NotAutorizedError(IndexedException):
    def __init__(self):
        super().__init__(-1002, 'You are not authorized to execute this request.')

class NoPermissionError(IndexedException):
    def __init__(self):
        super().__init__(-1003, 'You don\'t have permission to execute this request.')

class NoJsonError(IndexedException):
    def __init__(self):
        super().__init__(-1004, 'This request requires json to be send, but there was none or it was corrupted.')

class NotEnoughDataError(IndexedException):
    def __init__(self, sent: List[str], needed: List[str]):
        super().__init__(-1005, f'This request requires json to have next fields: {needed}, but got only: {sent}.')

class UserHasNoPhoneNumber(IndexedException):
    def __init__(self, user):
        super().__init__(-1006, f'User {user} can not select recall by phone number option as he has no phone number assigned to his account.')

class LotCreationError(IndexedException):
    def __init__(self, message):
        super().__init__(-1007, message)

class UserNotExists(IndexedException):
    def __init__(self, user):
        super().__init__(-1008, f'User {user} does not exist.')

class ModeratorAddingError(IndexedException):
    def __init__(self, message):
        super().__init__(-1009, message)

class JSONValueException(IndexedException):
    def __init__(self, param, avaited, got):
        super().__init__(-1010, f'Strange value got for {param}. Waited for {avaited} but got "{got}"')

class LotFiltrationError(IndexedException):
    def __init__(self, message):
        super().__init__(-1011, message)

class PasswordChangeException(IndexedException):
    def __init__(self, message):
        super().__init__(-1012, message)

class LotDeletionError(IndexedException):
    def __init__(self):
        super().__init__(-1013, 'You could not delete a lot that is not in an archive.')

class AccountRestoreError(IndexedException):
    def __init__(self, message):
        super().__init__(-1014, message)

class MaximumRequestsTimeout(IndexedException):
    def __init__(self, time_to_end: int):
        super().__init__(-1015, f'You made to much requests, wait at least {time_to_end} seconds to continue.')