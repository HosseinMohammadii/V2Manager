import math


def byte_to_gigabyte(b):
    return b / 1024 ** 3


def byte_to_megabyte(b):
    return b / 1024 ** 2


def gigabyte_to_byte(gb):
    return gb * (1024 ** 3)


def gigabyte_to_megabyte(gb):
    return gb * 1024
