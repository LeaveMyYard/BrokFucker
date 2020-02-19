from lib.database_handler import DatadaseHandler
from flask import Flask, abort, jsonify, request, make_response

class Lot:
    @staticmethod
    def approve(lot_id: int):
        database = DatadaseHandler()
        database.approve_lot(lot_id)

    @staticmethod
    def get_all_approved_lots():
        database = DatadaseHandler()
        return database.get_all_approved_lots()

    @staticmethod
    def get_all_unapproved_lots():
        database = DatadaseHandler()
        return database.get_all_unapproved_lots()

    @staticmethod
    def set_security_checked(lot_id: int, checked: bool):
        database = DatadaseHandler()
        database.set_security_checked(lot_id, checked)
