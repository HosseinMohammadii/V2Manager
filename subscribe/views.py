import base64
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_safe
from persiantools.jdatetime import JalaliDate

from sesame.utils import get_token, get_query_string, get_user as sesame_get_user

from utils.size import pretty_byte
from .models import Subscription

from .forms import BaseLoginForm, LoginForm




class FirstPage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "forbidden.html", status=403)
        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        if request.user.id != subs.owner.id:
            return render(request, "forbidden.html", status=403)
        auth_query_string = get_query_string(subs.owner, 'subs')
        confs_url = request.get_full_path()+"confs/"+auth_query_string
        return render(request, 'land.html', {'user_name': subs.user_name,
                                             'auth_query_string': auth_query_string,
                                             "confs_url": confs_url})


class Info(LoginRequiredMixin, View):
    raise_exception = False

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "forbidden.html", status=403)

        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        if request.user.id != subs.owner.id:
            return render(request, "forbidden.html", status=403)
        used_traffic = pretty_byte(subs.get_used_traffic())

        return render(request, 'info.html',
                      {"used_traffic": used_traffic,
                       "traffic": subs.traffic,
                       "jalali_expiredate": JalaliDate(subs.expire_date).strftime("%Y/%m/%d")})


class Confs(View):
    def get(self, request, *args, **kwargs):

        user = sesame_get_user(request, scope='subs')
        if user is None:
            raise PermissionDenied

        identifier = kwargs['id']
        subs = Subscription.objects.get(identifier=identifier)
        print(user, subs.owner)
        if user.id != subs.owner.id:
            raise PermissionDenied
        ressss = subs.get_edited_confs_uri()
        ressss = subs.get_all_confs_uri()
        return HttpResponse(ressss)


def login_view(request):
    if request.method == 'GET':
        form = BaseLoginForm()
        form2 = LoginForm()
        return render(request, 'login.html', {'form': form,
                                              'form2': form2,
                                              'resume': request.GET.get('next')})

    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            resume = form.cleaned_data['resume']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Hi {username.title()}, welcome back!')
                return redirect(resume)

        # form is not valid or user is not authenticated
        messages.error(request, f'نام کاربری یا رمز عبور اشتباه است. لطفا دوباره تلاش کنید.'
                                f'در صورت ادامه مشکل با پشتیبانی تماس بگیرید.')
        return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(request.GET.get('next', '/'))
