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
    is_minus = False
    if b < 0:
        b = -b
        is_minus = True

    if b == 0:
        return str(0) + " بایت "

    ret = None
    m = math.log2(b)
    if 0 < m < 10:
        bb = b
        ret = str(bb) + " بایت "
    if 10 < m < 20:
        bb = round(b / 1024, ndigits=3)
        ret = str(bb) + " کیلوبایت "
    if 20 < m < 30:
        bb = round(b / 1024 ** 2, ndigits=3)
        ret = str(bb) + " مگابایت "
    if 30 < m < 40:
        bb = round(b / 1024 ** 3, ndigits=3)
        ret = str(bb) + " گیگابایت "

    if is_minus:
        return '-' + ret

    return ret

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
