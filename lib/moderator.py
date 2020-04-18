from flask import Flask, abort, jsonify, request, make_response
import lib.util.exceptions as APIExceptions
from lib.user import User

class Moderator(User):
    @staticmethod
    @User.auth.verify_password
    def verify_user_password(email, password):
        try:
            user = Moderator(email)
        except APIExceptions.UserError:
            return False
        else:
            return user.check_password(password)

    def __init__(self, email):
        super().__init__(email)

        self.cursor.execute(
            f"SELECT `type` FROM Users WHERE `email` = ?",
            (email, )
        )
        res = self.cursor.fetchone()

        if res[0] < 1:
            raise APIExceptions.UserError("This user is not a moderator.")