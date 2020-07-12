import re


def validate_colour_code(value):
    regex = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
    return regex.match(value) != None
