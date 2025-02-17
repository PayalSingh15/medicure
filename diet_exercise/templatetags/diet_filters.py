from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary safely.
    Usage: {{ mydict|get_item:key }}
    """
    return dictionary.get(key, None)

@register.filter
def split(value, delimiter=','):
    """
    Splits a string into a list.
    Usage: {{ mystring|split:"," }}
    """
    return [x.strip() for x in value.split(delimiter)]