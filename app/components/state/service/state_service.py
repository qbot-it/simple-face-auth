from enum import Enum
from ...user.models.user import User


class Mode(Enum):
    AUTH = 1
    ADD = 2


class StateService:
    __mode: Mode
    __processing: bool
    __auth_active: bool
    __auth_user: User | None

    def __init__(self):
        self.__mode = Mode.AUTH
        self.__processing = False
        self.__auth_active = False
        self.__auth_user = None

    def get_mode(self) -> Mode:
        return self.__mode

    def get_auth_active(self) -> bool:
        return self.__auth_active

    def set_mode(self, mode: Mode):
        self.__mode = mode

    def set_auth_active(self, user: User):
        self.__auth_active = True
        self.__auth_user = user

    def set_auth_inactive(self):
        self.__auth_active = False
        self.__auth_user = None

    def set_processing(self, processing: bool):
        self.__processing = processing

    def is_processing(self) -> bool:
        return self.__processing

    def get_auth_user(self) -> User | None:
        return self.__auth_user
