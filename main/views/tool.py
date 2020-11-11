import json

from django.http import JsonResponse
from django.http import Http404


def idVarify(request):  # get, post, ajax
    """验证身份证号是否合法"""
    id_str = request.GET.get('id') or request.POST.get('id')
    if not id_str:
        raise Http404("ID number cannot be empty!")
    if len(id_str) != 18:
        raise Http404("ID number must be 18 digits!")
    WEIGHT = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1)
    id_strs = list(id_str)
    if id_strs[-1].lower() == 'x':
        id_strs[-1] = '10'
    id_ints = list(map(int, id_strs))
    products = [a * w for a, w in zip(id_ints, WEIGHT)]
    mod = sum(products) % 11
    is_valid = mod == 1
    data = {
        'valid': is_valid,
    }
    return JsonResponse(data)
