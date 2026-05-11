from django import template

register = template.Library()

def to_minutes(t):
    return t.hour * 60 + t.minute


@register.filter
def time_to_percent(t):
    start_day = 8 * 60   # 8 AM
    end_day = 22 * 60    # 10 PM

    total = end_day - start_day
    minutes = to_minutes(t) - start_day

    return max(0, (minutes / total) * 100)


@register.filter
def duration_to_percent(event):
    start = to_minutes(event["start"])
    end = to_minutes(event["end"])

    start_day = 8 * 60
    end_day = 22 * 60
    total = end_day - start_day

    duration = end - start

    return (duration / total) * 100