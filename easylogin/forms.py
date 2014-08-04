# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django import forms

from .auth import CodeLoginBackend

__all__ = ['CodeField', 'LoginForm']

class CodeField(forms.Field):
    def validate(self, value):
        backend = CodeLoginBackend()
        return backend.is_valid_code(code=value)


class LoginForm(forms.Form):
    code = CodeField()
    redirect_to = forms.URLField()
