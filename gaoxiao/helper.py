#!/usr/bin/env python
#coding=utf-8

"""
    helper.py

    :license: BSD, see LICENSE for more details.
"""

from functools import wraps
from flask import request, Response,render_template,url_for,redirect,session


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return redirect(url_for('frontend.login'))

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'name' in session:
            if not 'admin'==session['name']:
                return authenticate()
        else:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

