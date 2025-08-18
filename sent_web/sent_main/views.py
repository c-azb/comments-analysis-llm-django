

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect, render
import re
#from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.contrib import auth
from django.contrib import messages
from .forms import LoginForm,RegistrationForm

from overall_file_sent.views import sent_class
from . import settings

def home(request):
    if request.method == 'POST':
        test_input = request.POST['test_input']
        
        try:
            res = sent_class.process_pipe([test_input])[0]
            label = res['label']
            score = res['score']
            score = f'{float(score) * 100:.2f}'
        except Exception as e:
            label = e if settings.DEBUG else 'error'
            score = None
            

        context = {
            'label':label,
            'score':score
        }
        return render(request,'home.html',context)
    return render(request,'home.html')


def login_create_acc(request):
    if auth.get_user(request).is_authenticated:
        return redirect('home')

    login_form,registration_form = None,None
    
    if request.method == 'POST':
        if 'password2' in request.POST:
            registration_form = RegistrationForm(request.POST)
            if registration_form.is_valid():
                registration_form.save()
                username=registration_form.cleaned_data['username']
                password=registration_form.cleaned_data['password1']
                user = auth.authenticate(request, username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return redirect('home')
        else:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username_or_email = login_form.cleaned_data['username_or_email']
                password = login_form.cleaned_data['password']
                try:
                    user = CustomUser.objects.get(email=username_or_email)
                    username = user.username
                except CustomUser.DoesNotExist:
                    username = username_or_email

                user = auth.authenticate(request, username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, "Invalid credentials")
    context = {
        'login_form':login_form if login_form is not None else LoginForm(),
        'registration_form':registration_form if registration_form is not None else RegistrationForm()
    }
    return render(request,'login_create_acc.html',context)

def logout(request):
    auth.logout(request)
    return redirect('home')


    