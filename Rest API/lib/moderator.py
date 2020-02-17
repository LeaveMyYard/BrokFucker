from lib.database_handler import DatadaseHandler
from lib.user import User

class Moderator(User):
    @staticmethod
    @User.auth.verify_password
    def verify_password(email, password):
        database = DatadaseHandler()
        return database.check_password(email, password) and database.is_moderator(email)