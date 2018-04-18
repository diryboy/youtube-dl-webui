#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_login as lm
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

class AppUser(lm.UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField()

class UserManager(object):
    def __init__(self, secret_key, username, password):
        self.default_user = AppUser(secret_key)
        self.default_anonymous = lm.AnonymousUserMixin()
        self.username = username
        self.password = password

    def find_user_by_id(self, id):
        return self.default_user if id == self.default_user.get_id() else self.default_anonymous

    def find_user_by_form(self, form):
        return self.default_user if (form.username.data, form.password.data) == (self.username, self.password) else self.default_anonymous

    def no_user(self):
        return (self.username, self.password) == ('', '')
