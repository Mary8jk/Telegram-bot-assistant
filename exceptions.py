from http import HTTPStatus


class StatusException(Exception):
    pass


def set_robot_power(value):
    if HTTPStatus != HTTPStatus.OK:
        raise StatusException('Статус код отличен от 200.')
