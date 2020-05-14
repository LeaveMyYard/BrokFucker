'''
    Набор перечислений.
'''

from enum import Enum

class SubscriptionTypes(Enum):
    '''
        Типы подписок.
    '''

    Email = 0
    PhoneCall = 1
    