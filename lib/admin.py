from flask import Flask, abort, jsonify, request, make_response
from lib.moderator import Moderator, User, HTTPBasicAuth
import lib.util.exceptions as APIExceptions

class Admin(Moderator):
    auth = HTTPBasicAuth()
    auth.error_handler(User.unauthorized)

    @staticmethod
    @auth.verify_password
    def verify_user_password(email, password):
        print(f'Admin verify {email}, {password}')
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

        if res[0] < 2:
            raise APIExceptions.UserError("This user is not an administrator.")

    def add_moderator_rights(self, email):
        user = User(email)

        try:
            moderator = Moderator(email)
        except APIExceptions.UserError:
            pass
        else:
            raise APIExceptions.ModeratorAddingError(f'User {email} already has moderator rights.')
        
        self.cursor.execute(
            f"UPDATE Users SET `type` = 1 WHERE `email` = ?",
            (email, )
        )

        self.conn.commit()

    def remove_moderator_rights(self, email):
        user = User(email)

        try:
            Admin(email)
        except APIExceptions.UserError:
            pass
        else:
            raise APIExceptions.ModeratorAddingError('Could not remove moderator rights from an administrator.')

        try:
            moderator = Moderator(email)
        except APIExceptions.UserError:
            pass
        else:
            raise APIExceptions.ModeratorAddingError(f'User {email} is not a moderator.')
        
        self.cursor.execute(
            f"UPDATE Users SET `type` = 0 WHERE `email` = ?",
            (email, )
        )

        self.conn.commit()