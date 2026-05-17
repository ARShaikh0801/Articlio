from django import template
import re

register = template.Library()

@register.filter(name='lazy_images')
def lazy_images(value):
    """
    Injects loading="lazy" into all <img> tags in the given HTML string.
    Does not duplicate loading="lazy" if it already exists.
    """
    if not isinstance(value, str):
        return value
    return re.sub(r'<img\s+(?!.*?\bloading=)([^>]+)>', r'<img loading="lazy" \1>', value)
