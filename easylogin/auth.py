# -*- coding: utf-8 -*-
from __future__ import absolute_import

from collections import namedtuple

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from .util import import_string, get_provider

__all__ = ['CodeLoginBackend', 'get_backend']

PROVIDER = get_provider()

def get_backend():
    backend = getattr(settings, 'EASYLOGIN_AUTH_BACKEND')
    if isinstance(backend, basestring):
        backend = import_string(backend)
    if isinstance(backend, CodeLoginBackend):
        backend = CodeLoginBackend
    return backend

### Classes

class CodeLoginBackend(object):
    
    def __init__(self):
        super(CodeLoginBackend, self).__init__()
        self.provider = PROVIDER()

    def authenticate(self, easylogin_code=None, **kwargs):
        if code is None:
            return None
        if self.is_valid_code(code):
            user = self.provider.user_for_code(code)
            if self.provider.should_invalidate(code, user):
                self.provider.invalidate(code)
            self.set_backend(user)
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def is_valid_code(self, code):
        return self.provider.is_valid_code(code)
    
    def set_backend(self, user):
        if user is None:
            return
        module, name = self.__module__, self.__class__.__name__
        return user.backend = '%s.%s' % (module, name)
