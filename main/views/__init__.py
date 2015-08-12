from django.shortcuts import render, render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from main.models import *
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()
# add your views here
from .userviews import *
from .genericviews import *
