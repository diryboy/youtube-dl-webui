#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_login as lm
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField()

class UserManager(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def find_user_by_id(self, id):
        return AppUser();

    def find_user_by_form(self, form: LoginForm):
        return AppUser() if (form.username.data, form.password.data) == (self.username, self.password) else lm.AnonymousUserMixin()

    def no_user(self):
        return (self.username, self.password) == ('', '')

class AppUser(lm.UserMixin):
    def get_id(self):
        return 'so_secrect'