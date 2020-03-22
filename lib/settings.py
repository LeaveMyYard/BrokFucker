import json
from typing import Dict, Tuple, List

class Settings:
    @staticmethod
    def __load_settings() -> Dict:
        settings_file = open('settings.json', mode='r')
        return json.load(settings_file)

    @staticmethod
    def get_email_verification_link_base() -> str:
        return Settings.__load_settings()['email_verification_link_base']

    @staticmethod
    def get_smtp_data() -> Tuple[str, int, str, str]:
        d = Settings.__load_settings()['smtp_settings']
        return d['host'], d['port'], d['username'], d['password']

    @staticmethod
    def get_maximum_image_size() -> int:
        return Settings.__load_settings()['server_settings']['maximum_upload_file_size']

    @staticmethod
    def get_currency_settings() -> List[str]:
        return Settings.__load_settings()['lot_settings']['currency_types']