# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url
from easylogin.views import (QRCodeImageView, CodeLoginView,
        LoginFormView, CredentialsView)

__all__ = ['urlpatterns']

urlpatterns = patterns('easylogin.views',
    url(r'^credentials/?$', CredentialsView.as_view(), name="credentials"),
    url(r'^login/?$', LoginFormView.as_vie(), name="form_login"),
    url(r'^code/?$', CodeLoginView.as_vie(), name="code_login"),
    url(r'^qr/?$', gen_qr_code, name="qr"),
    )
