from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response
from lib.util.hash import sha256

class Lot:
    @staticmethod
    def approve(lot_id: int):
        database = DatabaseHandler()
        database.approve_lot(lot_id)

    @staticmethod
    def get_all_approved_lots():
        database = DatabaseHandler()
        return database.get_all_approved_lots()

    @staticmethod
    def get_all_unapproved_lots():
        database = DatabaseHandler()
        return database.get_all_unapproved_lots()

    @staticmethod
    def set_security_checked(lot_id: int, checked: bool):
        database = DatabaseHandler()
        database.set_security_checked(lot_id, checked)

    @staticmethod
    def get_lot(lot_id):
        database = DatabaseHandler()
        return database.get_lot(lot_id)

    @staticmethod
    def delete_lot(lot_id):
        database = DatabaseHandler()
        database.delete_lot(lot_id)

    @staticmethod
    def restore_lot(lot_id):
        database = DatabaseHandler()
        database.restore_lot(lot_id)

    @staticmethod
    def update_data(lot_id, field, value):
        database = DatabaseHandler()
        database.update_data(lot_id, field, value)

    @staticmethod
    def can_user_edit(user, lot_id):
        database = DatabaseHandler()
        return database.get_lot_creator(lot_id) == user

    @staticmethod
    def get_photos(lot_id):
        database = DatabaseHandler()
        return database.get_lot_photos(lot_id)
        
    @staticmethod
    def add_photo(image, lot_id):
        database = DatabaseHandler()
        return database.add_photo(image, lot_id)

    @staticmethod
    def remove_photo(lot_id, photo_id):
        database = DatabaseHandler()
        return database.remove_photo(lot_id, photo_id)

    @staticmethod
    def get_approved_subscriptions():
        database = DatabaseHandler()
        return database.get_approved_subscriptions()

    @staticmethod
    def get_unapproved_subscriptions():
        database = DatabaseHandler()
        return database.get_unapproved_subscriptions()