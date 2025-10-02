# store/templatetags/style_tags.py
from django import template
from ..data import STYLES

register = template.Library()

@register.simple_tag(takes_context=True)
def style_label(context, code):
    lang = context.get('LANG') or context['request'].COOKIES.get('language', 'ru')
    for s in STYLES:
        if s['code'] == code:
            return s['labels'].get(lang, s['labels'].get('en', code))
    return code