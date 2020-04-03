from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response
from lib.util.hash import sha256
from lib.settings import Settings
from typing import Dict
import lib.util.exceptions as APIExceptions
import os

class Lot:
    @staticmethod
    def check_filter(lot_filter: Dict) -> Dict:
        from app import RestAPI

        settings = Settings.get_lot_filter_settings()
        lot_settings = Settings.get_enter_settings()['lot']

        result_filter = {}

        available_types = settings['available_types']
        available_types['order_by'] = lot_settings.keys()
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
                raise APIExceptions.LotFiltrationError(f"show_only field in lot filtration should be a Map[str, List[str]]")

            result_filter['show_only'] = {}

            for key, value in lot_filter['show_only'].items():
                result_filter['show_only'][key] = value

                if key not in show_only:
                    raise APIExceptions.LotFiltrationError(f"{key} is not a valid group. Available groups are: {', '.join(show_only.keys())}")

                if not isinstance(value, list) or any([not isinstance(v, str) for v in value]):
                    raise APIExceptions.LotFiltrationError(f"show_only field in lot filtration should be a Map[str, List[str]]")

                for v in value:
                    if v not in show_only[key]:
                        raise APIExceptions.LotFiltrationError(f"{v} is not available for {key} group. Available values are: {', '.join(show_only[key])}")

        else:
            result_filter['show_only'] = None

        return result_filter

    def __init__(self, lot_id: int):
        self.database = DatabaseHandler()
        self.lot_id = lot_id

    @staticmethod
    def get_settings():
        return Settings.get_enter_settings()['lot']

    def approve(self):
        self.database.approve_lot(self.lot_id)

    def set_security_checked(self, checked: bool):
        self.database.set_security_checked(self.lot_id, checked)

    def get_lot_data(self):
        return self.database.get_lot(self.lot_id)

    def delete_lot(self):
        self.database.delete_lot(self.lot_id)

    def restore_lot(self):
        self.database.restore_lot(self.lot_id)

    def update_data(self, field, value):
        self.database.update_data(self.lot_id, field, value)

    def can_user_edit(self, user):
        return self.database.get_lot_creator(self.lot_id) == user

    def get_photos(self):
        return self.database.get_lot_photos(self.lot_id)
        
    def add_photo(self, image):
        return self.database.add_photo(image, self.lot_id)

    def remove_photo(self, photo_id):
        return self.database.remove_photo(self.lot_id, photo_id)

    def delete_entirely(self):
        if not self.database.is_lot_in_archive(self.lot_id):
            raise APIExceptions.LotDeletionError()

        photos_list = self.database.get_lot_photos_list(self.lot_id)

        for photo in photos_list:
            os.remove(f'data/images/lots/{photo}.jpg')

        self.database.delete_lot_data(self.lot_id)

    @staticmethod
    def get_favorites(user, lot_filter = None):
        database = DatabaseHandler()
        return database.get_favorites(user, lot_filter=Lot.check_filter(lot_filter))

    @staticmethod
    def get_personal(user, lot_filter = None):
        database = DatabaseHandler()
        return database.get_personal(user, lot_filter=Lot.check_filter(lot_filter))

    @staticmethod
    def get_personal_deleted(user, lot_filter = None):
        database = DatabaseHandler()
        return database.get_personal_deleted(user, lot_filter=Lot.check_filter(lot_filter))

    @staticmethod
    def get_all_approved_lots(lot_filter = None):
        database = DatabaseHandler()
        return database.get_all_approved_lots(lot_filter=Lot.check_filter(lot_filter))

    @staticmethod
    def get_all_unapproved_lots(lot_filter = None):
        database = DatabaseHandler()
        return database.get_all_unapproved_lots(lot_filter=Lot.check_filter(lot_filter))

    @staticmethod
    def get_approved_subscriptions():
        database = DatabaseHandler()
        return database.get_approved_subscriptions()

    @staticmethod
    def get_unapproved_subscriptions():
        database = DatabaseHandler()
        return database.get_unapproved_subscriptions()