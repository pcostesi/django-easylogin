from django.conf.urls.defaults import patterns, url
from easylogin.views import *


urlpatterns = patterns('easylogin.views',
    url(r'^credentials/?$', credentials_view, name="easylogin_credentials"),
    url(r'^login/?$', code_login, name="easylogin_code_login"),
    url(r'^qr/?$', gen_qr_code, name="easylogin_qr"),
    )