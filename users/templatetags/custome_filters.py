from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get an item from a dictionary in Django templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None  

