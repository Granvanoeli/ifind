# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from ifind.models import game_models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def profile_page(request, username):
    #return HttpResponse("wassup")
    u = User.objects.get(username=username)
    if u:
        user_profile = u.get_profile()
    #url = user_profile.url
    context = RequestContext(request, {})
    return render_to_response('profiles/profile_page.html', {'user_profile': u, 'profile': user_profile}, context)