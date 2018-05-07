from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, FormView
from accounts import forms

class Register(CreateView):
    form_class = forms.UserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/register.html"

class Login(FormView):
    form_class = forms.UserLoginForm

    def form_valid(self, form):
        print (form.cleaned_data['query'])
        username=form.cleaned_data['query']
        password=form.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
            return redirect('projects:all')
        else:
            return HttpResponse("Login Failed for unknown reason")

    template_name = "accounts/login.html"
    #success_url = reverse_lazy('projects:all')

class Logout(TemplateView):
    template_name = "home.html"

    def get(self, request):
        auth.logout(self.request)
        return render(self.request, template_name='home.html')
