#!/usr/bin/env python
#coding=utf-8

"""
    manager.py

    :license: BSD, see LICENSE for more details.
"""
import os
import sys
os.sys.path.append('E:\\Workstation\\Project\\gaoxiao\\')

from gaoxiao import create_app

if __name__ == '__main__':
    app = create_app("config.cfg")
    app.run('127.0.0.1', debug=True)
