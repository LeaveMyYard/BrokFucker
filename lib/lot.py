from lib.database_handler import DatabaseDrivenObject
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, abort, jsonify, request, make_response
from lib.util.hash import sha256
from lib.settings import Settings
from typing import Dict, Tuple
from datetime import datetime
import lib.util.exceptions as APIExceptions
import os

class Lot(DatabaseDrivenObject):
    @staticmethod
    def get_settings():
        return Settings.get_enter_settings()['lot']

    @staticmethod
    def serialize_lot(lot_data: Tuple):
        lot = Lot(lot_data[0])
        
        res = {
            'id': lot_data[0],
            'date': lot_data[1],
            'name': lot_data[2],
            'user': lot_data[3],
            'user_display_name': self.get_user_display_name(lot[3]),
            'user_avatar': self.get_user_avatar_link(lot[3]),
            'amount': lot_data[4],
            'currency': lot_data[5],
            'term': lot_data[6],
            'return_way': lot_data[7],
            'security': lot_data[8],
            'percentage': lot_data[9],
            'form': lot_data[10],
            'security_checked': eval(lot_data[11]),
            'guarantee_percentage': lot_data[12],
            'confirmed': eval(lot_data[13]),
            'commentary': lot_data[15],
            'photos': lot.get_photos(),
            'taken': lot.check_taken()
        }
        
        if lot.removed_by_moderator():
            res['remove_reason'] = lot.get_remove_reason()

        res['verification_requested'] = lot.security_verification_requested()
        res['club_guarantee_requested'] = lot.club_guarantee_requested()

        return res

    def __init__(self, lot_id: int):
        super().__init__()
        self.lot_id = lot_id

        if not self.exists(self.lot_id):
            raise APIExceptions.LotNotExistsError(self.lot_id)

    def club_guarantee_requested(self):
        self.cursor.execute(
            f"SELECT * FROM LotGuaranteeRequests WHERE `id` = ?",
            (self.lot_id,)
        )

        return self.cursor.fetchone() is not None

    def security_verification_requested(self):
        self.cursor.execute(
            f"SELECT * FROM LotSecurityVerificationRequests WHERE `id` = ?",
            (self.lot_id,)
        )

        return self.cursor.fetchone() is not None
    
    def get_remove_reason(self):
        self.cursor.execute(
            f"SELECT `reason` FROM LotVerificationDeclines WHERE `id` = ?",
            (self.lot_id, )
        )

        return self.cursor.fetchone()[0]

    def check_taken(self):
        self.cursor.execute(
            f"SELECT * FROM ConfirmedSubscriptions WHERE `lot` = ?",
            (self.lot_id, )
        )
        return self.cursor.fetchall() != []

    def get_photos_list(self):
        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )

        return eval(self.cursor.fetchone()[0])

    def get_photos(self):
        return {
            'lot_id': self.lot_id,
            'photos': [f'{request.host_url}image/lot/{photo}.jpg' for photo in self.get_photos_list()]
        }
    
    def exists(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `id` = ?",
            (lot_id, )
        )

        return self.cursor.fetchone() is not None

    def removed_by_moderator(self):
        self.cursor.execute(
            f"SELECT * FROM LotVerificationDeclines WHERE `id` = ?",
            (self.lot_id, )
        )

        return self.cursor.fetchall() != []

    def remove_moderator_delete_reason(self):
        self.cursor.execute(
            f"DELETE FROM LotVerificationDeclines WHERE `id` = ?",
            (self.lot_id, )
        )

        self.conn.commit()

    def approve(self):
        if self.removed_by_moderator():
            self.remove_moderator_delete_reason()

        self.cursor.execute(
            f"UPDATE Lots SET `confirmed` = 'True' WHERE `id` = ?",
            (self.lot_id, )
        )
        self.conn.commit()
        self.logger.info(f'New lot with id `{self.lot_id}` was approved')

    def unapprove(self):
        self.cursor.execute(
            f"UPDATE Lots SET `confirmed` = 'False' WHERE `id` = ?",
            (self.lot_id, )
        )
        self.conn.commit()

    def set_security_checked(self, checked: bool):
        self.cursor.execute(
            f"UPDATE Lots SET `security_checked` = ? WHERE `id` = ?",
            (str(checked), self.lot_id)
        )
        self.conn.commit()
        self.logger.debug(f'`Security checked` flag on lot with id `{self.lot_id}` is set to `{checked}`')

    def get_lot_data(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )
        lot = self.cursor.fetchone()

        return self.serialize_lot(lot)

    def delete_lot(self):
        self.cursor.execute(
            f"UPDATE Lots SET `deleted` = 'True' WHERE `id` = ?",
            (self.lot_id, )
        )
        self.conn.commit()

    def add_moderator_delete_reason(self, moderator, reason):
        if self.removed_by_moderator():
            self.remove_moderator_delete_reason()

        self.cursor.execute(
            f"INSERT INTO LotVerificationDeclines VALUES(?,?,?)",
            (self.lot_id, reason, moderator)
        )

        self.conn.commit()

    def delete_lot_by_moderator(self, moderator, reason):
        self.add_moderator_delete_reason(moderator, reason)
        self.delete_lot()

    def restore_lot(self):
        self.cursor.execute(
            f"UPDATE Lots SET `deleted` = 'False' WHERE `id` = ?",
            (self.lot_id, )
        )
        self.conn.commit()

    def update_data(self, field, value):
        self.unapprove()

        self.cursor.execute(
            f"UPDATE Lots SET `{field}` = ? WHERE `id` = ?",
            (value, self.lot_id)
        )
        self.conn.commit()

    def get_lot_creator(self):
        self.cursor.execute(
            f"SELECT `user` FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )

        return self.cursor.fetchone()[0]

    def can_user_edit(self, user):
        return self.get_lot_creator() == user
        
    def add_photo(self, image):
        self.unapprove()

        self.create_directory_if_not_exists('data/images/temp')
        self.create_directory_if_not_exists('data/images/lots')

        temporary_file_location = f'data/images/temp/{secure_filename(image.filename)}'
        image.save(temporary_file_location)

        im = Image.open(temporary_file_location)
        photo_hash = sha256(str(datetime.now()))
        file_location = f'data/images/lots/{photo_hash}.jpg'
        im = im.convert("RGB")
        im.save(file_location)

        os.remove(temporary_file_location)

        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )
        photos = eval(self.cursor.fetchone()[0])
        photos.append(photo_hash)

        stringified_photos = str(photos).replace('\'', '"')

        self.cursor.execute(
            f"UPDATE Lots SET `photos` = ? WHERE `id` = ?",
            (stringified_photos, self.lot_id)
        )
        self.conn.commit()

        return 'Photo is successfuly added.'

    def remove_photo(self, photo_id):
        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )

        photos: list = eval(self.cursor.fetchone()[0])
        photos.pop(photo_id)
        stringified_photos = str(photos).replace('\'', '"')

        self.cursor.execute(
            f"UPDATE Lots SET `photos` = ? WHERE `id` = ?",
            (stringified_photos, self.lot_id)
        )
        self.conn.commit()

        return 'Photo is successfuly removed.'

    def is_archived(self) -> bool:
        self.cursor.execute(
            f"SELECT `deleted` FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )

        return self.cursor.fetchone()[0] == 'True'

    def delete_entirely(self):
        if not self.is_archived():
            raise APIExceptions.LotDeletionError()

        photos_list = self.get_photos_list()

        for photo in photos_list:
            os.remove(f'data/images/lots/{photo}.jpg')

        self.delete_data()

    def delete_data(self):
        self.cursor.execute(
            f"DELETE FROM LotVerificationDeclines WHERE `id` = ?",
            (self.lot_id, )
        )

        self.cursor.execute(
            f"DELETE FROM Lots WHERE `id` = ?",
            (self.lot_id, )
        )

        self.conn.commit()

    def set_guarantee_value(self, value):
        self.cursor.execute(
            f"UPDATE Lots SET `guarantee_percentage` = ? WHERE `id` = ?",
            (value, self.lot_id)
        )

        self.conn.commit()

    def set_lot_guarantee_requested(self, requested: bool = True):
        if requested:
            self.cursor.execute(
                f"INSERT OR IGNORE INTO LotGuaranteeRequests VALUES(?)",
                (self.lot_id, )
            )
        else:
            self.cursor.execute(
                f"DELETE FROM LotGuaranteeRequests WHERE `id` = ?",
                (self.lot_id, )
            )

        self.conn.commit()

    def set_lot_security_verification_requested(self, requested: bool = True):
        if requested:
            self.cursor.execute(
                f"INSERT OR IGNORE INTO LotSecurityVerificationRequests VALUES(?)",
                (self.lot_id, )
            )
        else:
            self.cursor.execute(
                f"DELETE FROM LotSecurityVerificationRequests WHERE `id` = ?",
                (self.lot_id, )
            )

        self.conn.commit()

    def request_for_guarantee(self):
        self.set_lot_guarantee_requested()

    def request_for_security_verification(self):
        self.set_lot_security_verification_requested()

    def remove_request_for_guarantee(self):
        self.set_lot_guarantee_requested(requested=False)

    def remove_request_for_security_verification(self):
        self.set_lot_security_verification_requested(requested=False)

class LotListGatherer(DatabaseDrivenObject):
    @staticmethod
    def __check_filter(lot_filter: Dict) -> Dict:
        from app import RestAPI

        settings = Settings.get_lot_filter_settings()
        lot_settings = Settings.get_enter_settings()['lot']

        result_filter = {}

        available_types = settings['available_types']
        available_types['order_by'] = list(lot_settings.keys()) + ['user', 'date', 'guarantee_percentage']
        available_types['order_type'] = ['ASC', 'DESC']

        for value in available_types:
            result_filter[value] = str(lot_filter[value]) if value in lot_filter else None
            if result_filter[value] is not None:
                RestAPI.validate_field(value, result_filter[value], available_types[value])

        result_filter['limit'] = result_filter['limit'] or settings['maximum_length']

        # limit check
        if int(result_filter['limit']) > settings['maximum_length']:
            raise APIExceptions.LotFiltrationError(f"Could not load {lot_filter['limit']} lots. Maximum is {settings['maximum_length']}")

        show_only = {
            key: value for key, value in filter(lambda i: isinstance(i[1], list), lot_settings.items())
        }

        if 'show_only' in lot_filter:
            if not isinstance(lot_filter['show_only'], dict):
                raise APIExceptions.LotFiltrationError(f"show_only field in lot filtration should be a Map[str, List[str]], but got `{lot_filter['show_only']}`")

            result_filter['show_only'] = {}

            for key, value in lot_filter['show_only'].items():
                result_filter['show_only'][key] = value

                if key not in show_only:
                    raise APIExceptions.LotFiltrationError(f"{key} is not a valid group. Available groups are: {', '.join(show_only.keys())}")

                if not isinstance(value, list) or any([not isinstance(v, str) for v in value]):
                    raise APIExceptions.LotFiltrationError(f"show_only field in lot filtration should be a Map[str, List[str]], but got `{lot_filter['show_only']}`")

                for v in value:
                    if v not in show_only[key]:
                        raise APIExceptions.LotFiltrationError(f"{v} is not available for {key} group. Available values are: {', '.join(show_only[key])}")
            
            if result_filter['show_only'] == {}:
                result_filter['show_only'] = None
        else:
            result_filter['show_only'] = None

        return result_filter

    @staticmethod
    def __format_sql_lot_filter_string(lot_filter, where_is_already_used: bool = False) -> str:
        res = ""
        if lot_filter['show_only'] is not None:
            res += (' WHERE ' if not where_is_already_used else ' AND ') + ' AND '.join(
                [' OR '.join([f"`{type}` = '{value}'" for value in lot_filter['show_only'][type]]) for type in lot_filter['show_only']]
            )
        if lot_filter['order_by'] is not None:
            res += f" ORDER BY `{lot_filter['order_by']}` {lot_filter['order_type'] if lot_filter['order_type'] is not None else ''}"
        if lot_filter['limit'] is not None:
            res += f" LIMIT {lot_filter['limit']}"
        if lot_filter['offset'] is not None:
            res += f" OFFSET {lot_filter['offset']}"
        return res

    def __init__(self, lot_filter = {}):
        super().__init__()
        self.lot_filter = self.__check_filter(lot_filter)

    def get_requested_for_guarantee(self):
        self.cursor.execute(
            "SELECT * FROM LotsWithGuaranteeRequested" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_requested_for_security_verification(self):
        self.cursor.execute(
            "SELECT * FROM LotsWithSecurityVerificationRequested" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_all_approved_lots(self):
        self.cursor.execute(
            "SELECT * FROM LiveLots" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_all_unapproved_lots(self):
        self.cursor.execute(
            f"SELECT * FROM LiveUnacceptedLots" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_archive(self):
        self.cursor.execute(
            "SELECT * FROM ArchiveLatestLots" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_archived_history(self, lot_id):
        self.cursor.execute(
            "SELECT * FROM LotsArchive" + self.__format_sql_lot_filter_string(self.lot_filter)
        )

        table = self.cursor.fetchall()
        res_list = []

        for row in table:
            row = list(row)
            row[0], row[17] = row[17], row[0]
            res = Lot.serialize_lot(row)
            res['record_id'] = row[17]
            res['approve_date'] = row[18]
            res_list.append(res)

        return res_list

class UsersLotListGatherer(LotListGatherer):
    def __init__(self, user, lot_filter = {}):
        super().__init__(lot_filter=lot_filter)
        self.user = user

    def get_favorites(self):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?" +
            self.__format_sql_lot_filter_string(self.lot_filter, where_is_already_used=True), 
            (self.user, )
        )
        
        res: list = eval(self.cursor.fetchone()[0])

        return [Lot(lot_id).get_lot_data() for lot_id in reversed(res)]

    def get_personal(self):
        self.cursor.execute(
            "SELECT * FROM Lots" 
            "WHERE `user` = ? AND `deleted` = 'False' "
            "AND `id` NOT IN ConfirmedLots "
            "AND `id` NOT IN FinishedLots" +
            self.__format_sql_lot_filter_string(self.lot_filter, where_is_already_used=True),
            (self.user, )
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_personal_confirmed(self):
        self.cursor.execute(
            "SELECT * FROM Lots WHERE `user` = ? AND `deleted` = 'False' "
            "AND `id` IN ConfirmedLots " +
            self.__format_sql_lot_filter_string(self.lot_filter, where_is_already_used=True),
            (self.user, )
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_personal_finished(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `user` = ? AND `deleted` = 'False' "
            "AND `id` IN FinishedLots " +
            self.__format_sql_lot_filter_string(self.lot_filter, where_is_already_used=True),
            (self.user, )
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_personal_deleted(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `user` = ? and `deleted` = 'True'" + 
            self.__format_sql_lot_filter_string(self.lot_filter, where_is_already_used=True),
            (self.user, )
        )

        return [Lot.serialize_lot(lot) for lot in self.cursor.fetchall()]