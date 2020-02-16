class IndexedException(Exception):
    def __init__(self, id: int, message: str):
        self.error_id = id
        super().__init__(message)

    def __str__(self):
        return f'code({self.error_id}) {self.message}'

class RegistrationError(IndexedException):
    pass