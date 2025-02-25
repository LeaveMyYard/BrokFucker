'''
    Главный файл с настройками запросов для flask сервера.
'''

import json
import os
import re
from datetime import timedelta
from typing import Dict, List

from flask import (Flask, jsonify, make_response, request, send_file,
                   send_from_directory)
from flask_cors import CORS

import lib.util.exceptions as APIExceptions
from lib.admin import Admin
from lib.lot import Lot, LotListGatherer, UsersLotListGatherer
from lib.moderator import Moderator
from lib.settings import Settings
from lib.subscription import Subscription, SubscriptionListGatherer
from lib.user import User, UserRegistrator
from lib.util.decorators import weighted
from lib.util.logger import init_logger

APP = Flask(__name__, static_folder='admin/static')
CORS(APP)

LOGGER = init_logger(__name__)

APP.config['UPLOAD_FOLDER'] = 'data/images/upload'
APP.config['MAX_CONTENT_PATH'] = Settings.get_maximum_image_size()

class WebApp:
    '''
        Этот класс собирает набор статических методов, связанных с
        веб-сайтом.
    '''

    @staticmethod
    @APP.route('/')
    def root():
        '''
            Корень сайта на index.html
        '''

        return send_file('src/index.html')

    @staticmethod
    @APP.route('/<path:path>')
    def send_web(path):
        '''
            Все файлы вебсайта отсылаются с папки src
        '''

        if '.' not in path:
            return send_from_directory('src', path + '.html')
        return send_from_directory('src', path)

    @staticmethod
    @APP.route('/admin', defaults={'path': ''})
    @APP.route('/admin/<path:path>')
    def send_admin(path):
        '''
            Админ панель, написаная на React.
        '''

        if path != "" and os.path.exists(APP.static_folder + '/' + path):
            return send_from_directory(APP.static_folder, path)
        else:
            return send_from_directory('admin', 'index.html')

    # Also redirect all /image requests to data/images
    @staticmethod
    @APP.route('/image/lot/<path:path>')
    def send_lot_image(path):
        '''
            Переадресация фото лотов из папки с файлами.
        '''

        return send_from_directory('data/images/lots', path)

    @staticmethod
    @APP.route('/image/user/<path:path>')
    def send_user_image(path):
        '''
            Переадресация фото пользователей из папки с файлами.
        '''

        return send_from_directory('data/images/user', path)

    # Simplify the exceptions handlers.
    # Rather than definging a function for each error or code by hands we will
    # store all the possible ints and Exceptions as keys and
    # corresponding lambda functions as values.

    exceptions_responses = {
        404: lambda error: send_file('src/404.html')
    }

class RestAPI:
    '''
        RestAPI класс собирает некоторые методы, которые используются в API
        и набор некоторых функций, которые используются для этого.
    '''

    # -------------------------------------------------------------------------
    # Private stuff
    # -------------------------------------------------------------------------

    registration_handler = UserRegistrator()
    registration_handler.init_tables()
    registration_handler.run_verification_code_clearer(
        timedelta(hours=12),
        timedelta(days=7)
    )

    # Creating our own route decorator.
    # It will be almost the same as app.route except it will always be on '/api/v1/'
    route = lambda loc, **options: APP.route('/api/v1/' + loc, **options)

    # Simplify the exceptions handlers.
    # Rather than definging a function for each error or code by hands we will
    # store all the possible ints and Exceptions as keys and
    # corresponding lambda functions as values.
    exceptions_responses = {
        400: lambda error: {
            'code': -1000,
            'msg': 'An unknown error occured while processing the request.'
        },
        404: lambda error: {
            'code': -1001,
            'msg': 'The stuff you requested for is not found.'
        },
        APIExceptions.IndexedException: lambda error: {
            'code': error.error_id,
            'msg': error.args[0],
            'type': error.__class__.__name__
        },
    }

    @staticmethod
    def message(msg: str) -> str:
        '''
            Оборачивает строку в json строку ответа сервера.
        '''

        return jsonify(
            {
                'msg': msg
            }
        )

    @staticmethod
    def request_data_to_json(req) -> dict:
        '''
            Парсит данные из запроса в json.
            Используется вместо request.json так как
            flask не будет парсить json, если запросе
            не указано application/json.
        '''

        try:
            return json.loads(req)
        except json.decoder.JSONDecodeError:
            raise APIExceptions.NoJsonError()

    @staticmethod
    def check_required_fields(json_obj, data_required: List[str]) -> None:
        '''
            Проверяет необходимые значения в запросе.
            Если их нет, кинет ошибку.
        '''

        for data in data_required:
            if data not in json_obj:
                raise APIExceptions.NotEnoughDataError(data_required, json_obj.keys())

    @staticmethod
    def check_fields_values(json_obj: Dict, field_setting: str) -> None:
        '''
            Проверка значений полей.
        '''

        settings = Settings.get_enter_settings()[field_setting]
        for key, value in json_obj.items():
            if key not in settings:
                pass
            elif settings[key] is None:
                pass
            else:
                RestAPI.validate_field(key, value, settings[key])

    @staticmethod
    def validate_field(field_name, field_value, validation):
        '''
            Проверка значения поля.
        '''

        if isinstance(validation, str):
            if not re.fullmatch(validation, field_value):
                raise APIExceptions.JSONValueException(field_name, validation, field_value)
        elif isinstance(validation, list):
            if field_value not in validation:
                raise APIExceptions.JSONValueException(field_name, validation, field_value)

    # -------------------------------------------------------------------------
    # Public stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('ping', methods=['GET'])
    @weighted(weight=1)
    def ping():
        ''' Проверяет соединение с сервером.

        Проверяет соединение с Rest API.
        Возвращает простое сообщение "pong".'''

        return RestAPI.message('pong'), 200

    # -------------------------------------------------------------------------
    # Registration stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('register', methods=['POST'])
    @weighted(weight=10)
    def register():
        ''' Создать новый аккаунт.

        Запрос на создание нового аккаунта.
        Отправит письмо с подтверждением на почту, если такая почта существует.
        Иначе, выдаст ошибку.
        В письме с подтверждением будет ссылка, перейдя по которой
        браузер отправит запрос на подтверждение почты с кодом из сообщения.'''

        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'email',
            'password'
        ]

        for data in data_required:
            if data not in request_json:
                raise APIExceptions.NotEnoughDataError(data_required, request_json.keys())

        RestAPI.check_fields_values(request_json, "register")

        UserRegistrator().begin_email_verification(
            request_json['email'],
            request_json['password'],
        )

        return RestAPI.message(f"Verification is sent to {request_json['email']}"), 201

    @staticmethod
    @route('register/verify/<string:verification_hash>')
    @weighted(weight=2)
    def confirm_verification(verification_hash):
        ''' Подтвердить регистрацию.

        Подтверждает регистрацию по коду {verification_hash}.
        Ссылка с этим кодом присылается на почту пользователю:
        ./email_verification.html?code={verification_hash}

        При желании, эту ссылку можно изменить в настройках сервера,
        в файле settings.json, в параметре "email_verification_link_base".'''

        UserRegistrator().verify_email_confirmation(verification_hash)
        return RestAPI.message("Email was succesfully confirmed."), 201

    # -------------------------------------------------------------------------
    # User
    # -------------------------------------------------------------------------

    ### -----------------------------------------------------------------------
    ### Data
    ### -----------------------------------------------------------------------

    @staticmethod
    @route('user', methods=['GET'])
    @User.login_required
    @weighted(weight=1)
    def check_user():
        ''' Информация о текущем пользователе.

        Возвращает словарь с данными о текущем пользователе.'''

        user = User.current()
        return jsonify(user.get_data()), 200

    @staticmethod
    @route('user', methods=['PUT'])
    @User.login_required
    @weighted(weight=2)
    def edit_user_data():
        ''' Обновить данные текущего пользователя.

        Изменить параметры пользователя, такие как
        номер телефона и/или имя.'''

        request_json = RestAPI.request_data_to_json(request.data)

        data_required = {
            'phone': 'phone_number',
            'name': 'name',
        }

        RestAPI.check_fields_values(request_json, "user_data")

        user = User.current()
        for data in data_required:
            if data in request_json:
                user.edit_data(data_required[data], request_json[data])

        return RestAPI.message('Data is edited successfully.'), 201

    @staticmethod
    @route('user/password', methods=['PUT'])
    @User.login_required
    @weighted(weight=10)
    def change_password():
        ''' Запрос на изменение пароля пользователя.

        Отправляет запрос на изменение пароля.
        Подтверждение прийдет на почту пользователя с ссылкой,
        по аналогии с подтверждением почты.'''

        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'password'
        ]

        RestAPI.check_required_fields(request_json, data_required)
        RestAPI.check_fields_values(request_json, "register")

        user = User.current()

        user.change_password(request_json['password'])
        return RestAPI.message(f'Verification in sent to {user.email}.')

    @staticmethod
    @route('user/password/verify/<string:code>')
    @weighted(weight=2)
    def verify_password_code(code):
        ''' Подтвердить код изменения пароля.

        Подтверждает изменение пароля по коду.
        По аналогии с подтверждением почты, ссылка на файл, который сделает
        запрос автоматически, прийдет в сообщении на почту.'''

        UserRegistrator().verify_password_change(code)
        return RestAPI.message(f'Password was successfuly changed.')

    @staticmethod
    @route('user/restore/<string:email>')
    @weighted(weight=10)
    def restore_account(email):
        ''' Восстановить пароль.

        Запрос на восстановление(сброс) пароля.
        Подтверждение с кодом прийдет на почту, по аналогии
        с подтверждением почты.'''

        user = User(email)

        user.restore_account()
        return RestAPI.message(f'Verification in sent to {user.email}.')

    @staticmethod
    @route('user/restore/verify/<string:code>')
    @weighted(weight=2)
    def verify_account_restore(code):
        ''' Подтвердить восстановление пароля.

        По аналогии с двумя другими подтверждениями,
        подтверждает код, который прийдет на почту.
        После подтверждения, новый пароль будет выслан на почту.
        Рекомендуется сразу поменять его в профиле.'''

        UserRegistrator().verify_account_restore(code)
        return RestAPI.message(f'Temporary password is sent to your email.')

    ### -----------------------------------------------------------------------
    ### Avatar
    ### -----------------------------------------------------------------------

    @staticmethod
    @route('user/avatar', methods=['GET'])
    @User.login_required
    @weighted(weight=1)
    def get_avatar():
        ''' Ссылка на аватар текущего пользователя.

        Возвращает ссылку на аватар текущего пользователя.
        Если у него еще нет аватара, то вернется ссылка на
        аватар по умолчанию.'''

        user = User.current()
        return jsonify({'link': user.get_avatar_link()}), 200

    @staticmethod
    @route('user/avatar', methods=['POST'])
    @User.login_required
    @weighted(weight=2)
    def edit_avatar():
        ''' Загрузить новый аватар.

        Загружает аватар пользователя на сервер.
        Если у пользователя уже есть аватар, то он перезапишется.'''

        user = User.current()

        user.add_avatar(request.files['file'])
        return RestAPI.message('New avatar is saved.'), 201

    @staticmethod
    @route('user/avatar', methods=['DELETE'])
    @User.login_required
    @weighted(weight=2)
    def delete_avatar():
        ''' Удалить текущий аватар.

        Удаляет текущий аватар пользователя,
        замещая его аватаром по умолчанию.'''

        user = User.current()

        user.delete_avatar()
        return RestAPI.message('Your avatar is now deleted.'), 201

    # -------------------------------------------------------------------------
    # Lots stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('lots/settings', methods=['GET'])
    @weighted(weight=1)
    def get_lot_settings():
        ''' Информация о доступных значениях различных полей лотов.

        Возвращает значения параметров для лота.
        Существует три типа: str, List[str], None.
        В первом случае, это регулярное выражение.
        Во втором, это список позможных значений.
        В третьем это означает, что возможно
        произвольное строковое значение.

        Все эти значения хранятся в файле
        настроек сервера settings.json'''

        return jsonify(Lot.get_settings()), 200

    @staticmethod
    @route('lots/approved', methods=['GET', 'POST'])
    @route('lots', methods=['GET'])
    @weighted(weight=5)
    def get_approved_lots():
        ''' Получить все публичные лоты.

        Возвращает список лотов,
        которые доступны для публики.
        Это те лоты, которые прошли модерацию и
        еще не нашли своего спонсора.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении. '''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        lot_list = LotListGatherer(lot_filter)
        return jsonify(lot_list.get_all_approved_lots()), 200

    @staticmethod
    @route('lots', methods=['POST'])
    @User.login_required
    @weighted(weight=1)
    def create_lot():
        ''' Создать новый лот.

        Создает новый лот. Этот лот будет автоматически
        закреплен за текущим пользователем. По умолчанию,
        сразу после создания, лот будет отправлен на модерацию,
        где будет ожидать проверки.'''

        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'name',
            'amount',
            'currency',
            'term',
            'return_way',
            'security',
            'percentage',
            'form',
            'commentary'
        ]

        RestAPI.check_required_fields(request_json, data_required)
        RestAPI.check_fields_values(request_json, "lot")

        user = User.current()

        return jsonify({
            'lot_id': user.create_lot(*[request_json[data] for data in data_required])
        }), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['GET'])
    @weighted(weight=1)
    def get_lot(lot_id):
        ''' Получить данные о лоте.

        Получить данные о конкретном лоте по его айди.
        Лот возвращается стандартный словарь лота, как и в
        любом списке лотов.'''

        return jsonify(Lot(lot_id).get_lot_data()), 200

    @staticmethod
    @route('lots/<int:lot_id>', methods=['PUT'])
    @User.login_required
    @weighted(weight=3)
    def update_lot(lot_id):
        ''' Обновить данные лота.

        Изменить некоторые данные лота.
        Изменять данные лота может только его создатель.
        После изменения, если лот был подтвержден,
        он снова станет неподтвержденным и отправится
        на модерацию.'''

        lot = Lot(lot_id)
        user = User.current()

        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        request_json = RestAPI.request_data_to_json(request.data)

        data_available = [
            'name',
            'amount',
            'currency',
            'term',
            'return_way',
            'security',
            'percentage',
            'form',
            'commentary'
        ]

        RestAPI.check_fields_values(request_json, "lot")

        for data in data_available:
            if data in request_json:
                lot.update_data(data, request_json[data])

        return RestAPI.message('A lot is changed.'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['DELETE'])
    @User.login_required
    @weighted(weight=2)
    def delete_lot(lot_id):
        ''' Удалить лот.

        Переместить лот в архив.
        Архивный лот можно позже удалить полностью
        или восстановить.
        Эту операцию может делать только создатель лота.'''

        lot = Lot(lot_id)
        user = User.current()

        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        lot.delete_lot()
        return RestAPI.message('A lot is deleted.'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['POST'])
    @User.login_required
    @weighted(weight=2)
    def restore_lot(lot_id):
        ''' Восстановить удаленный лот.

        Если лот уже находится в архиве,
        восстановит его.
        Эту операцию может делать только создатель лота.'''

        lot = Lot(lot_id)
        user = User.current()
        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        lot.restore_lot()
        return RestAPI.message('A lot is restored.'), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['GET'])
    @weighted(weight=2)
    def get_lot_photos(lot_id):
        ''' Получить список фотографий лота.

        Возвращает список ссылок на фотографии лота по
        его айди.'''

        return jsonify({'link': Lot(lot_id).get_photos()}), 200

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['POST'])
    @User.login_required
    @weighted(weight=3)
    def add_lot_photo(lot_id):
        ''' Добавить лоту фотографию.

        Добавляет новую фотографию лоту.
        Это действие на подтвержденном лоте приведет
        к его повторной модерации.
        Эту операцию может делать только создатель лота.'''

        lot = Lot(lot_id)
        user = User.current()
        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        resp = {filename: lot.add_photo(request.files[filename]) for filename in request.files}

        return jsonify(resp), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos/<int:photo_id>', methods=['DELETE'])
    @User.login_required
    @weighted(weight=2)
    def remove_lot_photo(lot_id, photo_id):
        ''' Удалить фотографию лота.

        Удаляет фотографию лота по ее порядковому номеру.
        Это действие на подтвержденном лоте приведет
        к его повторной модерации.
        Эту операцию может делать только создатель лота.'''

        lot = Lot(lot_id)
        user = User.current()
        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        return jsonify(lot.remove_photo(photo_id)), 201

    @staticmethod
    @route('lots/favorites/<int:lot_id>', methods=['PUT'])
    @User.login_required
    @weighted(weight=1)
    def add_favorite_lot(lot_id):
        ''' Добавить лот в избранное.

        Добавляет выбранный лот в список избранных лотов пользователя.'''

        user = User.current()
        user.add_lot_to_favorites(lot_id)
        return RestAPI.message('A lot is added to favorites.'), 201

    @staticmethod
    @route('lots/favorites/<int:lot_id>', methods=['DELETE'])
    @User.login_required
    @weighted(weight=1)
    def remove_favorite_lot(lot_id):
        ''' Удалить лот из избранных.

        Удаляет выбранный лот из списка избранных лотов пользователя.'''

        user = User.current()
        user.remove_lot_from_favorites(lot_id)
        return RestAPI.message('A lot is removed from favorites.'), 201

    @staticmethod
    @route('lots/favorites', methods=['GET', 'POST'])
    @User.login_required
    @weighted(weight=3)
    def get_favorite_lots():
        ''' Получить список избранных лотов.

        Возвращает список избранных лотов пользователя.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        user = User.current()
        lot_list = UsersLotListGatherer(user, lot_filter)

        return jsonify(lot_list.get_favorites()), 200

    @staticmethod
    @route('lots/personal', methods=['GET', 'POST'])
    @route('lots/personal/current', methods=['GET', 'POST'])
    @User.login_required
    @weighted(weight=3)
    def get_personal_lots():
        ''' Получить список своих лотов.

        Возвращает список текущих лотов пользователя.
        В этом списке отсутствуют те лоты, которые
        являются заархивированными, нашедшими спонсора
        или завершенными.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        user = User.current()
        lot_list = UsersLotListGatherer(user, lot_filter)

        return jsonify(lot_list.get_personal()), 200

    @staticmethod
    @route('lots/personal/taken', methods=['GET', 'POST'])
    @User.login_required
    @weighted(weight=3)
    def get_personal_taken_lots():
        ''' Получить список своих лотов, нашедших финансирование.

        Возвращает список лотов пользователя, которые
        уже нашли финансирование.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        user = User.current()
        lot_list = UsersLotListGatherer(user, lot_filter)

        return jsonify(lot_list.get_personal_confirmed()), 200

    @staticmethod
    @route('lots/personal/finished', methods=['GET', 'POST'])
    @User.login_required
    @weighted(weight=3)
    def get_personal_finished_lots():
        ''' Получить список своих завершенных лотов.

        Возвращает список завершенных лотов пользователя.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        user = User.current()
        lot_list = UsersLotListGatherer(user, lot_filter)

        return jsonify(lot_list.get_personal_finished()), 200

    @staticmethod
    @route('lots/personal/deleted', methods=['GET', 'POST'])
    @User.login_required
    @weighted(weight=3)
    def get_personal_deleted_lots():
        ''' Получить список своих удаленных лотов.

        Возвращает архив лотов пользователя.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        user = User.current()
        lot_list = UsersLotListGatherer(user, lot_filter)

        return jsonify(lot_list.get_personal_deleted()), 200

    @staticmethod
    @route('lots/personal/deleted/<int:lot_id>', methods=['DELETE'])
    @User.login_required
    @weighted(weight=1)
    def delete_lot_entirely(lot_id):
        ''' Полностью удалить лот.

        Удаляет лот, если он уже находится в архиве.
        Эту операцию может делать только создатель лота.'''

        lot = Lot(lot_id)
        user = User.current()

        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        lot.delete_entirely()

        return RestAPI.message(f'Lot {lot_id} is now deleted from archive.')

    @staticmethod
    @route('lots/personal/<int:lot_id>/request/guarantee', methods=['PUT'])
    @User.login_required
    @weighted(weight=1)
    def request_club_guarantee(lot_id):
        ''' Запросить гарантию клуба.

        Запросить гарантию клуба для лота у модерации.
        Можно отправить value: boolean, которое, если является
        ложью, будет означать отмену запроса гарантии.'''

        lot = Lot(lot_id)
        user = User.current()

        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        try:
            value = RestAPI.request_data_to_json(request.data)['value']
        except (APIExceptions.NoJsonError, KeyError):
            value = True

        if value:
            lot.request_for_guarantee()
            return RestAPI.message('A request for a club garantee is sent.'), 201
        else:
            lot.remove_request_for_guarantee()
            return RestAPI.message('A request for a club garantee is now removed.'), 201

    @staticmethod
    @route('lots/personal/<int:lot_id>/request/verify_security', methods=['PUT'])
    @User.login_required
    @weighted(weight=1)
    def request_security_verification(lot_id):
        ''' Запросить подтверждение обеспечения.

        Запросить подтверждение обеспечения для лота у модерации.
        Можно отправить value: boolean, которое, если является
        ложью, будет означать отмену запроса подтверждения обеспечения.'''

        lot = Lot(lot_id)
        user = User.current()

        if not lot.can_user_edit(user):
            raise APIExceptions.NoPermissionError()

        try:
            value = RestAPI.request_data_to_json(request.data)['value']
        except (APIExceptions.NoJsonError, KeyError):
            value = True

        if value:
            lot.request_for_security_verification()
            return RestAPI.message('A request for a security verification is sent.'), 201
        else:
            lot.remove_request_for_security_verification()
            return RestAPI.message('A request for a security verification is now removed.'), 201

    @staticmethod
    @route('lots/subscription/<int:lot_id>', methods=['PUT'])
    @User.login_required
    @weighted(weight=1)
    def subscribe_to_lot(lot_id):
        ''' Подписаться на лот.

        Запросить у модерации подписку на лот.
        Передается тип обратной связи - type (Email или PhoneCall)
        и сообщение message, для модератора.'''

        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'type',
            'message',
        ]

        RestAPI.check_required_fields(request_json, data_required)
        user = User.current()

        if user.subscribe_to_lot(lot_id, *[request_json[data] for data in data_required]):
            return RestAPI.message(f'You are now subscribed to lot {lot_id}.'), 201
        else:
            return RestAPI.message('You are already subscribed.'), 200

    @staticmethod
    @route('lots/subscription/<int:lot_id>', methods=['DELETE'])
    @User.login_required
    @weighted(weight=1)
    def unsubscribe_from_lot(lot_id):
        ''' Убрать подписку на лот.

        Отменяет подписку на лот.
        Не возможно отменить подписку, если ее уже подтвердили.'''

        user = User.current()
        try:
            user.unsubscribe_from_lot(lot_id)
            return RestAPI.message(f'You are no longer subscribed to lot {lot_id}.'), 201
        except APIExceptions.SubscriptionManagementError:
            return RestAPI.message('You are not subscribed.'), 200

    @staticmethod
    @route('lots/subscription', methods=['GET'])
    @User.login_required
    @weighted(weight=2)
    def get_subscribed_lots():
        ''' Получить список лотов, на которые ты подписан.

        Возвращает список лотов, на которые ты подписан.
        Подписки не обязательно будут подтвержденными.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        user = User.current()
        return jsonify({'lots': SubscriptionListGatherer().get_from_user(user)}), 200

    # -------------------------------------------------------------------------
    # Moderator stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('lots/<int:lot_id>/approve', methods=['PUT'])
    @Moderator.login_required
    @weighted(weight=1)
    def approve_lot(lot_id):
        ''' Подтвердить лот.

        Подтверждает лот по айди.'''

        Lot(lot_id).approve()
        return RestAPI.message('A lot is now approved.'), 201

    @staticmethod
    @route('lots/<int:lot_id>/security', methods=['PUT'])
    @Moderator.login_required
    @weighted(weight=1)
    def set_security_checked(lot_id):
        ''' Подтвердить проверенное обеспечение лота.

        Устанавливает у лота проверенное обеспечение.'''

        lot = Lot(lot_id)
        lot.set_security_checked(True)
        lot.remove_request_for_security_verification()
        return RestAPI.message('Lot\'s security is now checked.'), 201

    @staticmethod
    @route('lots/<int:lot_id>/security', methods=['DELETE'])
    @Moderator.login_required
    @weighted(weight=1)
    def set_security_unchecked(lot_id):
        ''' Убрать проверенное обеспечение лота.

        Убирает у лота проверенное обеспечение.'''

        lot = Lot(lot_id)
        lot.set_security_checked(False)
        lot.remove_request_for_security_verification()
        return RestAPI.message('Lot\'s security is no more checked.'), 201

    @staticmethod
    @route('lots/<int:lot_id>/guarantee', methods=['PUT'])
    @Moderator.login_required
    @weighted(weight=1)
    def set_guarantee(lot_id):
        ''' Установить гарантию клуба лоту.

        Устанавливает лоту гарантию клуба.
        Гарантия клуба это целое число от 0 до 100
        включительно. Если это число 0, то считается,
        что у лота нет гарантии.'''

        request_json = RestAPI.request_data_to_json(request.data)
        RestAPI.check_required_fields(request_json, ['value'])

        value = request_json['value']
        lot = Lot(lot_id)
        lot.set_guarantee_value(value)
        lot.remove_request_for_guarantee()
        return RestAPI.message(f'Lot\'s guarantee is now {value}%.'), 201

    @staticmethod
    @route('lots/<int:lot_id>/guarantee', methods=['DELETE'])
    @Moderator.login_required
    @weighted(weight=1)
    def remove_guarantee(lot_id):
        ''' Убрать гарантию клуба у лота.

        Убирает у лота гарантию клуба.
        То есть, устанавливает ее значение равным 0.'''

        lot = Lot(lot_id)
        lot.set_guarantee_value(0)
        lot.remove_request_for_guarantee()
        return RestAPI.message('Lot\'s guarantee is now 0%.'), 201

    @staticmethod
    @route('lots/requested/guarantee', methods=['GET', 'POST'])
    @Moderator.login_required
    @weighted(weight=3)
    def get_guarantee_requested_lots():
        ''' Получить список лотов, запросивших гарантию клуба.

        Возвращает список лотов, владельцы которых запросили гарантию клуба.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении. '''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        lot_list = LotListGatherer(lot_filter)

        return jsonify(lot_list.get_requested_for_guarantee()), 200

    @staticmethod
    @route('lots/requested/security_verification', methods=['GET', 'POST'])
    @Moderator.login_required
    @weighted(weight=3)
    def get_security_requested_lots():
        ''' Получить список лотов, запросивших проверку обеспечения.

        Возвращает список лотов, владельцы которых запросили гарантию клуба.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        lot_list = LotListGatherer(lot_filter)

        return jsonify(lot_list.get_requested_for_security_verification()), 200

    @staticmethod
    @route('lots/unapproved', methods=['GET', 'POST'])
    @Moderator.login_required
    @weighted(weight=3)
    def get_unapproved_lots():
        ''' Получить список неподтвержденных лотов.

        Возвращает список лотов, которые еще не были подтверждены.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        lot_list = LotListGatherer(lot_filter)

        return jsonify(lot_list.get_all_unapproved_lots()), 200

    @staticmethod
    @route('lots/unapproved/<int:lot_id>', methods=['DELETE'])
    @Moderator.login_required
    @weighted(weight=1)
    def remove_unapproved_lot(lot_id):
        ''' Отклонить неподтвержденный лот.

        Отклонить модерацию неподтвержденного лота.
        Модератор должен отправить reason.
        У владельца данного лота вернется эта причина, а лот
        переместиться в архив автоматически.'''

        required_fields = ['reason']
        request_json = RestAPI.request_data_to_json(request.data)

        RestAPI.check_required_fields(request_json, required_fields)

        moderator = Moderator.current()
        reason = request_json['reason']
        lot = Lot(lot_id)
        lot.delete_lot_by_moderator(moderator, reason)

        return RestAPI.message(f'Lot {lot_id} is now removed for a reason: {reason}.')

    @staticmethod
    @route('lots/subscription/approved', methods=['GET'])
    @Moderator.login_required
    @weighted(weight=1)
    def get_approved_subscriptions():
        ''' Получить список подтвержденных подписок.

        Получить список подписок, которые подтвердил модератор,
        но которые еще не являются завершенными.'''

        return jsonify({'lots': SubscriptionListGatherer().get_approved()}), 200

    @staticmethod
    @route('lots/subscription/unapproved', methods=['GET'])
    @Moderator.login_required
    @weighted(weight=1)
    def get_unapproved_subscriptions():
        ''' Получить список неподтвержденных подписок.

        Получить список подписок, которые еще не были подтверждены.
        В этот список не будут входить те подписки, которые отправлены
        на лот, который уже нашел своего спонсора.'''

        return jsonify({'lots': SubscriptionListGatherer().get_unapproved()}), 200

    @staticmethod
    @route('lots/subscription/<string:sub_id>/approve', methods=['GET'])
    @Moderator.login_required
    @weighted(weight=1)
    def approve_subscription(sub_id):
        ''' Подтвердить неподтвержденную подписку.

        Подтвердить подписку из списка неподтвержденных подписок.'''

        subscription = Subscription(id)
        subscription.set_approved()
        return RestAPI.message(f'Subscription {sub_id} is now approved.'), 201

    @staticmethod
    @route('lots/subscription/<string:sub_id>/unapprove', methods=['GET'])
    @Moderator.login_required
    @weighted(weight=1)
    def unapprove_subscription(sub_id):
        ''' Снять подтверждение подписки.

        Убрать с подтвержденной подписки подтверждение.
        Автоматически, лот снова будет в поиске спонсора.'''

        subscription = Subscription(sub_id)
        subscription.set_approved(approved=False)
        return RestAPI.message(f'Subscription {sub_id} is now unapproved.'), 201

    @staticmethod
    @route('lots/subscription/<string:sub_id>', methods=['DELETE'])
    @Moderator.login_required
    @weighted(weight=1)
    def delete_subscription(sub_id):
        ''' Удалить неподтвержденную подписку.

        Удалить подписку, которая ожидает подтверждения.'''

        subscription = Subscription(sub_id)
        subscription.delete()
        return RestAPI.message(f'Subscription {sub_id} is now deleted.'), 201

    @staticmethod
    @route('lots/subscription/<string:sub_id>/finish', methods=['GET'])
    @Moderator.login_required
    @weighted(weight=1)
    def finish_subscription(sub_id):
        ''' Закончить подтвержденную подписку.

        Отметить подтвержденную подписку, как законченную.
        Соответственно, лот, на который ссылается подписка,
        так-же станет завершенным.'''

        subscription = Subscription(sub_id)
        subscription.finish()
        return RestAPI.message(f'Subscription {sub_id} is now finished.'), 201

    @staticmethod
    @route('lots/archive', methods=['GET', 'POST'])
    @Admin.login_required
    @weighted(weight=5)
    def get_lots_archive():
        ''' Получить список архивных лотов.

        Получить список лотов, которые были подтверждены когда-либо.
        Значение каждого соответствующего лота выводятся в последней по времени записи.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(LotListGatherer(lot_filter).get_archive()), 200

    @staticmethod
    @route('lots/archive/<int:lot_id>', methods=['GET', 'POST'])
    @Admin.login_required
    @weighted(weight=5)
    def get_lot_archive_history(lot_id):
        ''' Посмотреть историю архивного лота.

        Получить список лотов, каждый лот из которых
        является исторической записью лота по номеру lot_id.

        Как и в любом другом списке лотов, тут
        присутствует фильтрация.
        Это означает, что используя метод POST
        (для некоторых запросов, означает что-то другое)
        можно отправить параметр "filter", в котором
        нужно передать словарь, поддерживающий
        следующие значения:

        "limit" - число лотов в списке, максимум 1000.
        По умолчанию - 1000.

        "offset" - номер первого лота в списке
        (отступ от начала). По умолчанию - 0.

        "order_by" - имя поля, по которому необходимо
        сортировать список.

        "order_type" - тип сортировки, "ASC" или "DESC".
        По умолчанию - "ASC".

        "show_only" - словарь, в котором ключи - имена полей,
        по которым нужно делать фильтрацию. Поддерживаются
        только те поля, которые имеют в настройках
        формат List[str]. Значение же - список строк, где
        каждая строка - значение этого поля. В итоге запрос
        вернет только те лоты, значения полей которых,
        соответствуют данной фильтрации. То есть, для каждого
        ключа, будут отфильтрованы те лоты, значения
        соответствующего поля которого не находится в
        списке-значении.'''

        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(LotListGatherer(lot_filter).get_archived_history(lot_id)), 200

    # -------------------------------------------------------------------------
    # Admin stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('user/<string:email>/moderator', methods=['PUT', 'POST'])
    @Admin.login_required
    @weighted(weight=1)
    def give_moderator_rights(email):
        ''' Добавить права модератора

        Изменяет статус пользователя с почтой email на "moderator".'''

        admin = Admin.current()
        admin.add_moderator_rights(email)
        return RestAPI.message(f'{email} is now a moderator.')

    @staticmethod
    @route('user/<string:email>/moderator', methods=['DELETE'])
    @Admin.login_required
    @weighted(weight=1)
    def remove_moderator_rights(email):
        ''' Убрать права модератора

        Изменяет статус пользователя с почтой email на "user".'''

        admin = Admin.current()
        admin.remove_moderator_rights(email)
        return RestAPI.message(f'{email} is no longer a moderator.')

class Server:
    '''
        Общая обработка ошибок сервера из WebApp и RestAPI.
    '''

    @staticmethod
    def process_exception(ex, error):
        '''
            Если ошибка в /api/, обрабатывает как ошибку API.
            Иначе, обрабатывает как ошибку сайта.
        '''

        if not request.path.startswith('/api/') and ex in WebApp.exceptions_responses:
            LOGGER.error('Website error %s: %s', ex, error)
            return WebApp.exceptions_responses[ex](error), ex if isinstance(ex, int) else 403
        elif ex in RestAPI.exceptions_responses:
            LOGGER.error('RestAPI error %s: %s', ex, error)
            return make_response(
                jsonify(
                    RestAPI.exceptions_responses[ex](error)
                ),
                ex if isinstance(ex, int) else 403
            )

    exceptions = set(WebApp.exceptions_responses) | set(RestAPI.exceptions_responses)

    # This one is just to prevent errors appearing in VSCode
    # Actually there is no error, just IDE being buged
    ex = None

    for ex in exceptions:
        @staticmethod
        @APP.errorhandler(ex)
        def _error_handler(error, exception=ex):
            return Server.process_exception(exception, error)

if __name__ == '__main__':
    APP.run(debug=True)
