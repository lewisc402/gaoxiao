#! /usr/bin/env python
#coding=utf-8
"""
    __init__.py

    :license: BSD, see LICENSE for more details.
"""

import os
import logging
import sys

from flask import Flask, g, session, request, flash, redirect, jsonify, url_for
from mongokit import Connection

from gaoxiao.models import *
from gaoxiao.views import *

DEFAULT_MODULES = (
        (frontend, ""),
        (admin, "/admin"))

DEFAULT_APP_NAME = 'gaoxiao'

def create_app(config=None, modules=None):

    if modules is None:
        modules = DEFAULT_MODULES

    app = Flask(DEFAULT_APP_NAME)

    #config
    app.config.from_pyfile(config)
    configure_db(app)
    #configure_extensions(app)

    #configure_logging(app)
    #configure_errorhandlers(app)
    #configure_before_handlers(app)
    #configure_template_filters(app)
    #configure_context_processors(app)
    #configure_signals(app)
    #babel = Babel(app)

    # register module
    configure_modules(app, modules)

    return app

def configure_db(app):
    pass

def configure_modules(app, modules):

    for module, url_prefix in modules:
        app.register_module(module, url_prefix=url_prefix)

