'''
    Набор декораторов
'''

from datetime import datetime, timedelta
from threading import Timer

import lib.util.exceptions as APIExceptions
from lib.settings import Settings
from lib.util.logger import init_logger
from app import request

LOGGER = init_logger(__name__)

IP_WEIGHTS = {
    '1s': {},
    '1m': {},
    '1h': {}
}

BAN_LIST = {}

MAX_WEIGHTS = Settings.get_max_weights()

def _remove_1s():
    IP_WEIGHTS['1s'] = {}
    timer = Timer(1.0, _remove_1s)
    timer.start()

def _remove_1m():
    IP_WEIGHTS['1m'] = {}
    timer = Timer(60.0, _remove_1m)
    timer.start()

def _remove_1h():
    IP_WEIGHTS['1h'] = {}
    timer = Timer(3600.0, _remove_1h)
    timer.start()

_remove_1s()
_remove_1m()
_remove_1h()

def weighted(weight):
    '''
        Функция, которая возвращает декоратор.
        Каждый раз, когда это функция будет вызываться, будет смотреть,
        с какого айпи был сделан запрос и считать количество запросов с
        этого айпи. Если количество запросов слишком большое, даст этому
        айпи софт-бан.
    '''

    def decorator(func):
        def res_func(*args, **kwargs):
            request_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

            LOGGER.debug(
                "Request from %s with weight %s.",
                request_ip,
                weight
            )

            if request_ip in BAN_LIST:
                duration = BAN_LIST[request_ip][0] - datetime.now()
                if duration < timedelta(seconds=0):
                    BAN_LIST.pop(request_ip)
                else:
                    raise APIExceptions.MaximumRequestsTimeout(
                        time_to_end=int((BAN_LIST[request_ip][0] - datetime.now()).total_seconds())
                    )

            ban_durations = [
                timedelta(minutes=5),
                timedelta(minutes=15),
                timedelta(hours=1),
                timedelta(days=1)
            ]

            for key, values in IP_WEIGHTS.items():
                if request_ip not in values:
                    values[request_ip] = 0
                if values[request_ip] > MAX_WEIGHTS[key]:
                    BAN_LIST[request_ip] = [
                        datetime.now(),
                        (BAN_LIST[request_ip][1] if request_ip in BAN_LIST else []) +
                        [datetime.now()]
                    ]
                    BAN_LIST[request_ip][1] = ban_cases = list(
                        filter(
                            lambda time: (
                                time > datetime.now() - timedelta(days=1),
                                BAN_LIST[request_ip][1]
                            )
                        )
                    )

                    for stats in IP_WEIGHTS:
                        IP_WEIGHTS[stats][request_ip] = 0

                    ban_time = ban_durations[len(ban_cases) - 1]
                    BAN_LIST[request_ip][0] = datetime.now() + ban_time

                    LOGGER.warning("User %s was banned for %s", request_ip, ban_time)
                    raise APIExceptions.MaximumRequestsTimeout(int(ban_time.total_seconds()))
                values[request_ip] += weight

            LOGGER.debug(
                "Stats: (1s: %s, 1m: %s, 1h: %s)",
                IP_WEIGHTS['1s'][request_ip],
                IP_WEIGHTS['1m'][request_ip],
                IP_WEIGHTS['1h'][request_ip]
            )

            return func(*args, **kwargs)

        res_func.__name__ = func.__name__

        return res_func
    return decorator
