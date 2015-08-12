from django.shortcuts import render_to_response
from django.http import HttpResponse

# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    return render_to_response("msg.html", context);

def returnJson(dict):
    if dict:
        return HttpResponse(json.dumps(dict), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'error':'returnJson() input dict is empty'}, content_type='application/json')
