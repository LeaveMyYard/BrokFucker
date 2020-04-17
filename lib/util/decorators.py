from lib.util.logger import init_logger
from threading import Timer
from lib.settings import Settings
from datetime import datetime, timedelta
import lib.util.exceptions as APIExceptions

logger = init_logger(__name__)

ip_weights = {
    '1s': {},
    '1m': {},
    '1h': {}
}

ban_list = {}

max_weights = Settings.get_max_weights()

def remove_1s():
    ip_weights['1s'] = {}
    t = Timer(1.0, remove_1s)
    t.start()

def remove_1m():
    ip_weights['1m'] = {}
    t = Timer(60.0, remove_1m)
    t.start()

def remove_1h():
    ip_weights['1h'] = {}
    t = Timer(3600.0, remove_1h)
    t.start()

remove_1s()
remove_1m()
remove_1h()

def weighted(weight):
    from app import request

    def decorator(func):
        def res_func(*args, **kwargs):
            request_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

            logger.debug(f"Request from {request_ip} with weight {weight}.")

            if request_ip in ban_list:
                duration = ban_list[request_ip][0] - datetime.now()
                if duration < timedelta(seconds=0):
                    ban_list.pop(request_ip)
                else:
                    raise APIExceptions.MaximumRequestsTimeout(time_to_end=int((ban_list[request_ip][0] - datetime.now()).total_seconds()))

            ban_durations = [timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=1), timedelta(days=1)]
            
            for key, values in ip_weights.items():
                if request_ip not in values:
                    values[request_ip] = 0
                if values[request_ip] > max_weights[key]:
                    ban_list[request_ip] = [datetime.now(), (ban_list[request_ip][1] if request_ip in ban_list else []) + [datetime.now()]]
                    ban_list[request_ip][1] = ban_cases = list(filter(lambda time: time > datetime.now() - timedelta(days=1), ban_list[request_ip][1]))

                    for stats in ip_weights:
                        ip_weights[stats][request_ip] = 0

                    ban_time = ban_durations[len(ban_cases) - 1]
                    ban_list[request_ip][0] = datetime.now() + ban_time

                    logger.warning(f"User {request_ip} was banned for {ban_time}")
                    raise APIExceptions.MaximumRequestsTimeout(int(ban_time.total_seconds()))
                values[request_ip] += weight

            logger.debug(f"Stats: (1s: {ip_weights['1s'][request_ip]}, 1m: {ip_weights['1m'][request_ip]}, 1h: {ip_weights['1h'][request_ip]})")

            return func(*args, **kwargs)

        res_func.__name__ = func.__name__

        return res_func
    return decorator