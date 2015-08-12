from django.shortcuts import render_to_response

# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    return render_to_response("msg.html", context);
