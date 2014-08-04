# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import get_current_site


try:
    from django.utils.module_loading import import_string
except ImportError:
    import_string = None


try:
    if not import_string:
        from django.utils.module_loading import import_by_path as import_string
except ImportError:
    from django.utils.importlib import import_module

    def import_string(path):
        i = path.rfind('.')
        module, attr = path[:i], path[i + 1:]
        mod = import_module(module)
        return getattr(mod, attr)


def get_host_domain(request):
    try:
        return get_current_site(request).domain
    except:
        return request.get_host()

def get_provider():
    CODE_PROVIDER = getattr(settings, 'EASYLOGIN_CODE_PROVIDER')
    if isinstance(CODE_PROVIDER, basestring):
        return import_string(CODE_PROVIDER)
    if CODE_PROVIDER:
        return CODE_PROVIDER
    raise ImproperlyConfigured('Missing EASYLOGIN_CODE_PROVIDER in settings')
