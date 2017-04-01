from django.utils import timezone


def formatDate(dt, mode="optimize"):
    if mode == 'optimize':  # [2015-]12-05 11:25 am
        time_format = '%m-%d %H:%M %p'
        if dt.year != timezone.now().year:
            time_format = '%Y-' + time_format
    elif mode == 'dateonly':  # 12-05
        time_format = '%m-%d'
    elif mode == 'fulldateonly':  # 2015-12-05
        time_format = '%Y-%m-%d'
    elif mode == 'timeonly':
        time_format = '%H:%M:%S'
    else:
        time_format = '%Y-%m-%d %H:%M %p'
    return dt.astimezone(timezone.get_current_timezone()).strftime(time_format)


def formatTimedelta(td, mode="full"):
    # get data
    d = td.days
    h = td.seconds // (60 * 60)
    m = td.seconds % (60 * 60) // 60
    s = td.seconds % 60
    days = '{d}天'.format(d=d)
    hours = '{h}小时'.format(h=h)
    minutes = '{m}分'.format(m=m)
    seconds = '{s}秒'.format(s=s)
    # parse mode
    if mode == 'full':  # 1天 11小时 7分 22秒
        mode = '%d %H %M %S'
    elif mode == 'largest':
        mode = '%d' if d else ('%H' if h else ('%M' if m else '%S'))
    result = mode
    result = result.replace('%d', days if d else '').replace('%H', hours if h else '').replace('%M', minutes).replace('%S', seconds).strip()
    # return
    if not result:
        result = str(td)
    return result


def formatDateToNow(dt, mode='full'):
    surfix = '前' if dt < timezone.now() else '后'
    delta = abs(dt - timezone.now())
    return formatTimedelta(delta, mode) + surfix
