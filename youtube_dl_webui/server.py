#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import flask_login as lm
import user as um

from flask import Flask
from flask import render_template
from flask import request, redirect, abort
from multiprocessing import Process
from copy import deepcopy

MSG = None
user_manager = None

app = Flask(__name__)

app.config.from_envvar('YOUTUBE_DL_WEBUI_APP_SETTINGS_FILE')

login_manager = lm.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return user_manager.find_user_by_id(userid)

MSG_INVALID_REQUEST = {'status': 'error', 'errmsg': 'invalid request'}

@app.route("/login", methods=["GET", "POST"])
def login():
    if user_manager.no_user():
        lm.login_user(user_manager.find_user_by_id(None))
        return redirect('/')

    form = um.LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", form=form)
    else:
        user = user_manager.find_user_by_form(form)
        if user.is_authenticated:
            lm.login_user(user)
            return redirect("/")
        else:
            return login_manager.unauthorized()

@app.route("/logout")
def logout():
    lm.logout_user()
    return redirect("/login")

@app.route('/')
@lm.login_required
def index():
    return render_template('index.html')

@app.route('/task', methods=['POST'])
@lm.login_required
def add_task():
    payload = request.get_json()

    MSG.put('create', payload)
    return json.dumps(MSG.get())


@app.route('/task/list', methods=['GET'])
@lm.login_required
def list_task():
    payload = {}
    exerpt = request.args.get('exerpt', None)
    if exerpt is None:
        payload['exerpt'] = False
    else:
        payload['exerpt'] = True

    payload['state'] = request.args.get('state', 'all')

    MSG.put('list', payload)
    return json.dumps(MSG.get())


@app.route('/task/state_counter', methods=['GET'])
@lm.login_required
def list_state():
    MSG.put('state', None)
    return json.dumps(MSG.get())


@app.route('/task/batch/<action>', methods=['POST'])
@lm.login_required
def task_batch(action):
    payload={'act': action, 'detail': request.get_json()}

    MSG.put('batch', payload)
    return json.dumps(MSG.get())

@app.route('/task/tid/<tid>', methods=['DELETE'])
@lm.login_required
def delete_task(tid):
    del_flag = request.args.get('del_file', False)
    payload = {}
    payload['tid'] = tid
    payload['del_file'] = False if del_flag is False else True

    MSG.put('delete', payload)
    return json.dumps(MSG.get())


@app.route('/task/tid/<tid>', methods=['PUT'])
@lm.login_required
def manipulate_task(tid):
    payload = {}
    payload['tid'] = tid

    act = request.args.get('act', None)
    if act == 'pause':
        payload['act'] = 'pause'
    elif act == 'resume':
        payload['act'] = 'resume'
    else:
        return json.dumps(MSG_INVALID_REQUEST)

    MSG.put('manipulate', payload)
    return json.dumps(MSG.get())


@app.route('/task/tid/<tid>/status', methods=['GET'])
@lm.login_required
def query_task(tid):
    payload = {}
    payload['tid'] = tid

    exerpt = request.args.get('exerpt', None)
    if exerpt is None:
        payload['exerpt'] = False
    else:
        payload['exerpt'] = True

    MSG.put('query', payload)
    return json.dumps(MSG.get())


@app.route('/config', methods=['GET', 'POST'])
@lm.login_required
def get_config():
    payload = {}
    if request.method == 'POST':
        payload['act'] = 'update'
        payload['param'] = request.get_json()
    else:
        payload['act'] = 'get'

    MSG.put('config', payload)
    return json.dumps(MSG.get())


###
# test cases
###
@app.route('/test/<case>')
def test(case):
    return render_template('test/{}.html'.format(case))


class Server(Process):
    def __init__(self, msg_cli, usr_mgr: um.UserManager, host, port):
        super(Server, self).__init__()

        self.MSG = msg_cli
        self.user_manager = usr_mgr
        self.host = host
        self.port = port

    def run(self):
        global MSG, user_manager
        MSG, user_manager = self.MSG, self.user_manager

        app.run(host=self.host, port=int(self.port), use_reloader=False)


