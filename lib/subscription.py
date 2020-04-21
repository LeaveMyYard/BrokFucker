from lib.database_handler import DatabaseDrivenObject
import lib.util.exceptions as APIExceptions
from enum import Enum
from lib.util.enums import SubscriptionTypes

class Subscription(DatabaseDrivenObject):
    class Status(Enum):
        NotConfirmed = 1
        Confirmed = 2
        Finished = 3

    def __init__(self, id: int):
        super().__init__()
        self.id = id

    def set_approved(self, approved=True):
        self.cursor.execute(
            f"UPDATE SubscriptionRequests SET `confirmed` = ? WHERE `id` = ?",
            (str(approved), self.id)
        )

        self.conn.commit()

    def get_status(self):
        self.cursor.execute(
            f"SELECT `confirmed`, `finished` FROM SubscriptionRequests WHERE `id` = ?",
            (id, )
        )

        confirmed, finished = self.cursor.fetchone()
        confirmed, finished = eval(confirmed), eval(finished)

        if finished:
            return Subscription.Status.Finished
        elif confirmed:
            return Subscription.Status.Confirmed
        else:
            return Subscription.Status.NotConfirmed

    def delete(self):
        status = self.get_status()

        if status != Subscription.Status.NotConfirmed:
            raise APIExceptions.SubscriptionManagementError(f'Could not delete subscription with status {status.name()}')
        
        self.cursor.execute(
            f"DELETE FROM SubscriptionRequests WHERE `id` = ?",
            (self.id, )
        )

        self.conn.commit()

    def finish(self, finished: bool = True):
        status = self.get_status()

        if status != Subscription.Status.Confirmed:
            raise APIExceptions.SubscriptionManagementError(f'Could not finish subscription with status {status.name()}')

        self.cursor.execute(
            f"UPDATE SubscriptionRequests SET `finished` = ? WHERE `id` = ?",
            (str(finished), self.id)
        )

        self.conn.commit()

class SubscriptionListGatherer(DatabaseDrivenObject):
    def get_approved(self):
        self.cursor.execute(
            f"SELECT * FROM ConfirmedSubscriptions"
        )

        return [
            {
                'id': id, 
                'user': user, 
                'lot': lot, 
                'type': SubscriptionTypes(type).name, 
                'message': message
            } 
            for id, user, lot, type, message in self.cursor.fetchall()
        ]

    def get_unapproved(self):
        self.cursor.execute(
            f"SELECT * FROM UnconfirmedSubscriptions"
        )

        return [
            {
                'id': id, 
                'user': user, 
                'lot': lot, 
                'type': SubscriptionTypes(type).name, 
                'message': message
            } 
            for id, user, lot, type, message in self.cursor.fetchall()
        ]

    def get_from_user(self, user):
        self.cursor.execute(
            f"SELECT `lot`, `confirmed`, `type`, `message` FROM SubscriptionRequests WHERE `user` = ?",
            (user.email, )
        )

        return [
            {
                'id': id, 
                'user': user, 
                'lot': lot, 
                'type': SubscriptionTypes(type).name, 
                'message': message
            } 
            for id, user, lot, type, message in self.cursor.fetchall()
        ]

    def get_finished(self):
        self.cursor.execute(
            f"SELECT * FROM FinishedSubscriptions"
        )
        
        return [
            {
                'id': id, 
                'user': user, 
                'lot': lot, 
                'type': SubscriptionTypes(type).name, 
                'message': message
            } 
            for id, user, lot, type, message in self.cursor.fetchall()
        ]
