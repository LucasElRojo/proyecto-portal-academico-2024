# templatetags/custom_tags.py
from django import template

register = template.Library()

@register.simple_tag
def build_key(student_id, n):
    return f'{student_id}_{n}'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
