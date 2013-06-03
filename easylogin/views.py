from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from easylogin.auth import generate_code, AUTH_CODE_TIMEOUT
from django.conf import settings
from django.template.loader import render_to_string
from django.http import QueryDict

import qrcode

LOGIN_TEMPLATE = getattr(settings, "EASYLOGIN_LOGIN_TEMPLATE", "login.html")
SUCCESS_REDIRECT = getattr(settings, "EASYLOGIN_REDIRECT_ON_SUCCESS", "/")
ERROR_TEMPLATE = getattr(settings, "EASYLOGIN_ERROR_TEMPLATE", "error.html")


def make_query_url(url, query):
    encoded = QueryDict('', mutable=True)
    encoded.update(query)
    return "%s?%s" % (url, encoded.urlencode())

@login_required
def gen_qr_code(request):
    auth_code = request.GET.get("authCode")
    if not auth_code:
        auth_code = generate_code(request.user)
    current_site = get_current_site(request)
    scheme = request.is_secure() and "https" or "http"
    login_link = "".join([
        scheme,
        "://",
        current_site.domain,
        reverse("easylogin_code_login", args=(auth_code,)),
    ])
    img = qrcode.make(login_link)
    response = HttpResponse(mimetype="image/png")
    img.save(response, "PNG")
    return response

def code_login(request, auth_code):
    user = authenticate(code=auth_code)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse(SUCCESS_REDIRECT))
    txt = render_to_string(ERROR_TEMPLATE, {"auth_code": auth_code})
    return HttpResponseForbidden(txt)

@login_required
def credentials_view(request):
    auth_code = generate_code(request.user)
    render_to_response(LOGIN_TEMPLATE, {
        "user": request.user,
        "auth_code": auth_code,
        "expires_in": AUTH_CODE_TIMEOUT,
        "qr_url": make_query_url(
            reverse("easylogin_qr"),
            {"authCode": auth_code})
        })