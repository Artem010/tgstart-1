from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

from django.db import models

from users.models import User

from django import forms

class UserForm(forms.Form):
    username= forms.CharField(max_length=100)
    first_name= forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    tg_id = forms.CharField(max_length=100)



def auth(request):
    submitbutton= request.POST.get("submit")

    username=''
    first_name=''
    last_name=''
    tg_id=''

    if request.method == "POST":
        print('NEW request!!')



    form= UserForm(request.POST or None)
    if form.is_valid():



        currentUser = User.objects.filter(tg_id=form.cleaned_data.get("tg_id")).exists()
        if not currentUser:
            username= form.cleaned_data.get("username")
            first_name= form.cleaned_data.get("first_name")
            last_name= form.cleaned_data.get("last_name")
            tg_id= form.cleaned_data.get("tg_id")
            a = User(user_name = username, user_firstname=first_name, user_lastname=last_name, tg_id =tg_id)
            a.save()
        currentUser = User.objects.filter(tg_id=form.cleaned_data.get("tg_id"))
        # print(currentUser[0].id)

        request.session['mainUserId'] = currentUser[0].id
        return redirect('/dashboard')


    context= {'form': form, 'username': username, 'first_name': first_name, 'last_name': last_name, 'submitbutton': submitbutton}

    return render(request, 'users/auth.html', context)



def index(request):

    sessionUserId=request.session.get('mainUserId')
    if sessionUserId != None:
        return redirect('/dashboard')
    return render(request, 'volt/index.html')


def logout(request):
    del request.session['mainUserId']
    print("*******del session*******")
    return redirect('/')
