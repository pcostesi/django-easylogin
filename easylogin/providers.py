# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from hmac import new as new_hmac
from time import time

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.cache.backends.base import InvalidCacheBackendError
from django.utils.crypto import pbkdf2


__all__ = ['Provider', 'NineNumbersProvider']

def get_cache():
    try:
        try:
            from django.core.cache import caches
            return caches['easylogin']
        except ImportError:
            from django.core.cache import get_cache as django_get_cache
            return django_get_cache('easylogin')
    except InvalidCacheBackendError:
        from django.core.cache import cache
        return cache




class Provider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def code_for_user(self, user):
        pass

    @abstractmethod
    def user_for_code(self, code):
        pass

    @abstractmethod
    def invalidate(self, code):
        pass

    @abstractmethod
    def should_invalidate(self, code, user=None):
        pass

    @abstractmethod
    def is_valid_code(self, code):
        pass


class NineNumbersProvider(Provider):
    VALIDITY = 30
    CACHE_PREFIX = 'EASYLOGIN_NNP_'
    LEN = 9

    def __init__(self):
        self.store = get_cache()

    def code_for_user(self, user):
        # derive a code for the user
        code = self.__derive_code(user)
        # derive a key for the code
        key = self.__derive_key(code)
        # set the user (value) to the key in the store
        self.store.set(key, user, NineNumbersProvider.VALIDITY)
        return code

    def __derive_code(self, user):
        CODE_MAX = 10 ** NineNumbersProvider.LEN
        SUB_KEY = 6
        data = unicode(user.get_username()) + ':' + str(user.password)
        data += unicode(user.last_login)
        salt = self.__get_time_seed()
        salt += str(user.password).zfill(SUB_KEY)[-1 * SUB_KEY:]
        iterations = PBKDF2PasswordHasher.iterations
        code = int(pbkdf2(data, salt, iterations), 16)
        while code > CODE_MAX:
            code = (code / CODE_MAX) ^ (code % CODE_MAX)
        return str(code).zfill(NineNumbersProvider.LEN)

    def __derive_key(self, code):
        hmac_digest = new_hmac(code + self.__get_time_seed()).hexdigest()
        return '%s%s' % (NineNumbersProvider.CACHE_PREFIX, hmac_digest)

    def __get_time_seed(self):
        return '%d' % (time() / NineNumbersProvider.VALIDITY)

    def user_for_code(self, code):
        # derive a key for this code
        key = self.__derive_key(code)
        # fetch the user from the store
        return self.cache.get(key)

    def inavlidate(self, code):
        # expunge the key from the store
        key = self.__derive_key(code)
        self.store.delete(key)

    def should_invalidate(self, code, user=None):
        return True

    def is_valid_code(self, code):
        # get the user for this code
        # then derive a second code
        # and if both match, return True
        pass
