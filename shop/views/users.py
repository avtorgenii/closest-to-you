from django.contrib.auth.views import LoginView
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.defaults import page_not_found

from shop.forms import LoginUserForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'shop/users/login.html'
    extra_context = {'title': 'Authorization'}

    def get_success_url(self):
        # Get the user who just logged in
        user = self.request.user

        # Check if the user is a client
        if hasattr(user, 'client_profile'):
            return reverse_lazy('client_dashboard')

        # Check if the user is a worker
        elif hasattr(user, 'worker_profile'):
            worker = user.worker_profile
            if worker.role.name == 'Support':
                return reverse_lazy('support_dashboard')

        raise Http404('Page not found XD')


