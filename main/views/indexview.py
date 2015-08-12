from django.shortcuts import render_to_response
from util.ctrl import *

# Create your views here.
def index(request):
    return render_to_response('index/index.html');
