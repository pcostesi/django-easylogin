from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from time import time


AUTH_CODE_TIMEOUT = getattr(settings, "AUTH_CODE_TIMEOUT", 60)
AUTH_CODE_SALT = getattr(settings, "AUTH_CODE_SALT", settings.SECRET_KEY)
AUTH_CODE_FORMATTERS = getattr(settings, "AUTH_CODE_FORMATTERS", [])


def _gen_user_key(user):
    return "AUTH-EASYLOGIN-%d" % (user.id,)

def _gen_auth_key(code):
    return "AUTH-EASYLOGIN-TOKEN-%s" % (code,)

def _get_timestamp():
    tf = time()
    ts = int(tf)
    return str(ts - (ts % AUTH_CODE_TIMEOUT))

def generate_access_codes(user):
    ts = _get_timestamp()
    codes = [formatter(user, salt, ts) for formatter in AUTH_CODE_FORMATTERS]
    formatted_codes = dict([(_gen_auth_key(code), user) for code in codes])
    cache.set_many(formatted_codes, AUTH_CODE_TIMEOUT)
    cache.set(_gen_user_key(user), codes, AUTH_CODE_TIMEOUT)
    return codes

def generate_code(user):
    try:
        return generate_access_codes(user)[0]
    except IndexError:
        return None

def _get_user(*codes):
    for code in codes:
        user = cache.get(_gen_auth_key(code))
        if user:
            return user

def consume_access_code(*codes):
    user = _get_user(*codes)
    if user:
        all_codes = cache.get(_gen_user_key(user))
        cache.delete_many(all_codes)
        cache.delete(_gen_user_key(user))
    return user


class CodeLoginBackend(object):
    def authenticate(self, code=None, codes=None, **kwargs):
        if code is None and codes is None:
            return None
        codes = codes or [code]
        return consume_access_code(*codes)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
