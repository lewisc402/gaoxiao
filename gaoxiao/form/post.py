#!/usr/bin/env python
#coding=utf-8

"""
    post.py
    ~~~~~~~~~~~~~

    :license: BSD, see LICENSE for more details.
"""
from flaskext.wtf import Form, TextAreaField, FileField, SubmitField, TextField, PasswordField, \
            HiddenField, required, url, email, AnyOf

#from flaskext.babel import gettext, lazy_gettext as _

class LoginForm(Form):
    username = TextField(("Username"), validators=[required("this field is required")])
    password = PasswordField(("Password"))
    next = HiddenField()
    submit = SubmitField(("Login"))

class SignupForm(Form):
    username = TextField(("Username"), validators=[
                         required(message=("Username required"))])
    password = PasswordField(("Password"), validators=[
                             required(message=("Password required"))])
    email = TextField(("Email address"), validators=[
                      required(message=("Email address required")),
                      email(message=("A valid email address is required"))])
    code = TextField(("Signup Code"), validators=[AnyOf('test', message='code is not valid')])
    next = HiddenField()
    submit = SubmitField(("Signup"))

class PostForm(Form):
    title = TextField(("title"), validators=[required("this field is required")])
    text = TextAreaField(("text"))
    file = FileField(("file"))
    submit = SubmitField(("Post"))

class CommentForm(Form):
    name = TextField(("Name"), validators=[required("this field is required")])
    email = TextField(("Email"), validators=[
                      required(message=("Email required")),
                      email(message=("A valid email address is required"))])
    comment = TextAreaField(("Comment"), validators=[
                      required(message=("Comment required"))])

    submit = SubmitField(("Submit"))


