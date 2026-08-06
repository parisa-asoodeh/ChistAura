from django import template

register = template.Library()


@register.filter
def duration(seconds):

    if seconds is None:
        return "-"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes:02d}:{remaining_seconds:02d}"