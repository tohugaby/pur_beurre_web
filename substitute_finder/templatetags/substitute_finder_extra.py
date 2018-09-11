from django import template


register = template.Library()


@register.filter
def range_tag(value, min=0):
    """
    tag that return a range
    """
    if value:
        return range(min, value)
    return range(min)
