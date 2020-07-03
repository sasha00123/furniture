from django import template
import emoji

register = template.Library()


def num_to_emoji(number):
    if 1 <= number <= 10:
        return emoji.emojize(f":keycap_{number}:")

    return ''.join([emoji.emojize(f":keycap_{digit}:") for digit in str(number)])


@register.filter
def emojize(number):
    number = int(number)

    if number == 1:
        return emoji.emojize(":1st_place_medal:")
    elif number == 2:
        return emoji.emojize(":2nd_place_medal:")
    elif number == 3:
        return emoji.emojize(":3rd_place_medal:")

    return num_to_emoji(number)
