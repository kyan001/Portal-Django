# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    return render_to_response("msg.html", context);

# Create your views here.
def index(request):
    return render_to_response('index/index.html');


