# buy_sell/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

'''

@register.filter
def paginate_segments(segments, page_num):
    # Implement pagination logic here
    return segments[10*(page_num-1):10*page_num]
'''