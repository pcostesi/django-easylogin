from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse as django_reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

import qrcode

from .forms import LoginForm
from .auth import get_backend
from .util import get_host_domain, get_provider

__all__ = ['QRCodeImageView', 'CodeLoginView',
           'LoginFormView', 'CredentialsView']

PROVIDER = get_provider()
DEFAULT_REDIRECT = getattr(settings, 'EASYLOGIN_DEFAULT_REDIRECT', '/')
CREDENTIALS_TEMPLATE = getattr(settings, 'EASYLOGIN_CREDENTIALS_TEMPLATE',
    'easylogin/credentials.html')
LOGIN_TEMPLATE = getattr(settings, 'EASYLOGIN_LOGIN_TEMPLATE',
    'easylogin/login.html')
ERROR_TEMPLATE = getattr(settings, 'EASYLOGIN_ERROR_TEMPLATE',
    'easylogin/error.html')


### Util functions for generating urls and responses
def _make_query_url(url, **kwargs):
    return '%s?%s' % (url, urlencode(**kwargs))

def reverse(target, **query):
    if not query:
        return django_reverse(target)
    return _make_query_url(django_reverse(target), query)

def render_to_forbidden(*args, **kwargs):
    response = render_to_response(*args, **kwargs)
    response.status_code = 403
    return response


### Class based views

class LoginRequiredView(View):
    def __init__(self, *args, **kwargs):
        super(CredentialsView, self).__init__(*args, **kwargs)
        self.provider = PROVIDER()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)


class QRCodeImageView(LoginRequiredView):
    def get_url_for_code(self, auth_code):
        current_site = get_host_domain(request)
        scheme = 'https' if request.is_secure() else 'http'
        return u''.join([
            scheme,
            '://',
            current_site,
            reverse('easylogin:form_login', code=auth_code),
        ])

    def generate_image(self, auth_code=None, fmt=None):
        request = self.request
        if not fmt: fmt = 'PNG'
        if not auth_code:
            auth_code = self.provider.code_for_user(request.user)
        return qrcode.make(self.get_url_for_code(auth_code)

    def get(self, request, fmt=None):
        auth_code = request.GET.get('code')
        response = HttpResponse(mimetype='image/%s' % fmt)
        img = self.generate_image(auth_code, fmt)
        img.save(response, fmt)
        return response


class CodeLoginView(View):
    def __init__(self, *args, **kwargs):
        super(CodeLoginView, self).__init__(*args, **kwargs)
        self.backend = get_backend()

    def get(self, request):
        auth_code = request.GET.get('code')
        redirect_to = request.GET.get('redirect_to', DEFAULT_REDIRECT)
        return self.login(request, auth_code, redirect_to)

    def login(self, request, auth_code, redirect_to):
        user = self.backend.authenticate(easylogin_code=auth_code)
        if user is not None:
            if user.is_active:
                logout(request)
                login(request, user)
                return HttpResponseRedirect(redirect_to)

        return render_to_forbidden(ERROR_TEMPLATE,
            {'auth_code': auth_code})


class LoginFormView(CodeLoginView, FormView):
    form = LoginForm
    template_name = LOGIN_TEMPLATE

    def get_initial(self):
        params = self.request.GET
        initial = {
                'code': params.get('code'),
                'redirect_to': params.get('redirect_to'),
                }
        return initial

    def form_valid(self): 
        user = self.backend.authenticate(easylogin_code=self.form.code)
        logout(request)
        login(self.request, user)
        return HttpReponseRedirect(self.form.redirect_to)

    def form_invalid(self):
        ctx = {
            'auth_code': self.form.code,
            'form': self.form,
            'redirect_to': self.form.redirect_to
            }
        return render_to_forbidden(ERROR_TEMPLATE, ctx)

    def get_success_url(self):
        return self.form.redirect_to


class CredentialsView(TemplateView, LoginRequiredView):
    template_name = CREDENTIALS_TEMPLATE

    def get_context_data(self, **kwargs):
        ctx = super(CredentialsView, self).get_context_data(self, **kwargs)
        auth_code = self.provider.code_for_user(request.user)
        ctx.update({
            'user': self.request.user,
            'auth_code': auth_code,
            'qr_url': reverse('easylogin:qr', code=auth_code),
            })
