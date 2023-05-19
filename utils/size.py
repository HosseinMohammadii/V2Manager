import math
from hurry.filesize import size


byte_size_system = [
    (1024 ** 5, ' Megamanys'),
    (1024 ** 4, ' ترابایت'),
    (1024 ** 3, ' گیگابایت'),
    (1024 ** 2, ' مگابایت'),
    (1024 ** 1, ' کیلوبایت'),
    (1024 ** 0, ' بایت'),
]


def pretty_byte(b):
    return size(b, system=byte_size_system)


def pretty_megabyte(b):
    return pretty_byte(megabyte_to_byte(b))


def byte_to_gigabyte(b):
    return b / 1024 ** 3


def byte_to_megabyte(b):
    return b / 1024 ** 2


def gigabyte_to_byte(gb):
    return gb * (1024 ** 3)


def megabyte_to_byte(gb):
    return gb * (1024 ** 2)


def gigabyte_to_megabyte(gb):
    return gb * 1024
