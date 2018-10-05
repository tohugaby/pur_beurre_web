"""
substitute_finder app custom templatetags module
"""
from django import template

register = template.Library()


@register.filter
def range_tag(value, min_value=0):
    """
    tag that return a range
    """
    if value:
        return range(min_value, value)
    return range(min_value)
