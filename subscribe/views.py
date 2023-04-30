import base64
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from hurry.filesize import size

import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_safe
from persiantools.jdatetime import JalaliDate

from .models import Subscription

my_size_system = [
    (1024 ** 5, ' Megamanys'),
    (1024 ** 4, ' ترابایت'),
    (1024 ** 3, ' گیگابایت'),
    (1024 ** 2, ' مگابایت'),
    (1024 ** 1, ' کیلوبایت'),
    (1024 ** 0, ' بایت'),
]


class FirstPage(View):
    def get(self, request, *args, **kwargs):
        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        return render(request, 'land.html', {'user_name': subs.user_name})


class Info(View):
    def get(self, request, *args, **kwargs):
        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        used_traffic = size(subs.get_traffic(), system=my_size_system)
        return render(request, 'info.html',
                      {"used_traffic": used_traffic,
                       "traffic": subs.traffic,
                       "jalali_expiredate": JalaliDate(subs.expire_date).strftime("%Y/%m/%d")})


class Confs(View):
    def get(self, request, *args, **kwargs):
        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        all_conf = subs.get_original_confs()
        # print(all_conf)
        # for c in all_conf:
        #     print(c)

        ressss = subs.get_edited_confs_uri()
        return HttpResponse(ressss)
        # return render(request, 'info.html', {"conf_text": conf_text})


from .forms import LoginForm


def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Hi {username.title()}, welcome back!')
                return redirect('posts')

        # form is not valid or user is not authenticated
        messages.error(request, f'Invalid username or password')
        return render(request, 'login.html', {'form': form})
