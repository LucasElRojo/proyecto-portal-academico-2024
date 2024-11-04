# apps/templatetags/user_groups.py
from django import template

register = template.Library()

@register.filter
def in_group(user, group_id):
    """
    Verifica si el usuario pertenece a un grupo específico por ID.
    Uso en el template: {% if user|in_group:4 %}
    """
    return user.groups.filter(id=group_id).exists()