from django import template
register = template.Library()


@register.filter
def isurl(value):
    input_string = str(value)
    protocals = ['http', 'ftp', 'https', 'file', 'magnet', 'thunder', 'ed2k']
    for p in protocals:
        if input_string.startswith(p + '://'):
            return True
    return False
