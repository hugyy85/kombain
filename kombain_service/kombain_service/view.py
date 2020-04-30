from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth import login, authenticate, logout, views as auth_views
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required()
def home(request):
    return render(request, 'base.html')


def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_pwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_pwd)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/sign_up.html', {'form': form})

