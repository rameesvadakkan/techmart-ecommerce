from django import template

register = template.Library()

@register.filter
def average(ratings):
    total = 0
    count = ratings.count()

    if count == 0:
        return 0

    for r in ratings:
        total += r.rating

    return round(total / count, 1)

