import json
from sys import argv
import secrets
import os
from PIL import Image
from flask import url_for
from flask_app.models import Movements, Users, UserTestScores, ComponentMovements, Components, Workouts
from flask_app import db, mail, app
from flask_mail import Message
from flask_bcrypt import generate_password_hash
from datetime import datetime


def save_pic(picture):
    rand_hex = secrets.token_hex(8)
    f, e = os.path.splitext(picture.filename)
    pic_name = rand_hex + f + '.jpg'
    pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_name)
    print('pic path ', pic_path)
    size = (125, 125)
    with Image.open(picture) as f:
        try:
            f.thumbnail(size)
            f.save(pic_path, 'JPEG')
        except OSError:
            print('cannot convert', picture)
    return pic_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password visit the following string:
{url_for("reset_password", token = token, _external = True)}

If you did not submit this request ignore this email and no changes will be made.
"""
    mail.send(msg)


'''class Movements():
    def __init__(self, id, name, upper, lower, full, push, pull, total, kind):
        self.id = id
        self.name = name
        self.upper = upper
        self.lower = lower
        self.full = full
        self.push = push
        self.pull = pull
        self.total = total
        self.kind = kind
'''


def users_import(file):
    if not file:
        return ' please provide file path'
    with open('C:/Users/owner/IdeaProjects/gymsitev2/flask_app/DB/users.json') as f:
        data = json.load(f)

        for i in range(len(data['rows'])):
            if data['rows'][i][-1] == '1':
                data['rows'][i][-1] = True
            else:
                data['rows'][i][-1] = False

            user = Users(id=data['rows'][i][0], name='None', username=data['rows'][i][1], email=data['rows'][i]
                         [2], password=generate_password_hash(data['rows'][i][4], rounds=10).decode('utf-8'), profile_pic=data['rows'][i][3], is_admin=data['rows'][i][5])
            db.session.add(user)
            db.session.commit()
            print(user.name)


def movements_import(file):
    if not file:
        return ' please provide file path'
    with open(file) as f:
        data = json.load(f)

        for i in range(len(data['rows'])):
            for x in range(2, 8):
                # print(x, data['rows'][i][x])
                if data['rows'][i][x] == '1':
                    data['rows'][i][x] = True
                else:
                    data['rows'][i][x] = False

            move = Movements(id=data['rows'][i][0], name=data['rows'][i][1], upper=data['rows'][i][2], lower=data['rows'][i][3],
                             full=data['rows'][i][4], push=data['rows'][i][5], pull=data['rows'][i][6], total=data['rows'][i][7], kind=data['rows'][i][8])
            db.session.add(move)
            db.session.commit()
            print(move.name)


def score_import(file):
    if not file:
        return ' please provide file path'
    with open(file) as f:
        data = json.load(f)

        for i in range(len(data['rows'])):
            anext_id = int(data['rows'][i][0])
            acheck = UserTestScores.query.get(anext_id)
            while acheck:
                anext_id += 51
                acheck = Movements.query.get(anext_id)

            load = UserTestScores(id=anext_id, user_id=data['rows'][i][1],
                                  move_id=data['rows'][i][2], score=data['rows'][i][3], score_type='lbs')

            db.session.add(load)
            db.session.commit()

        for i in range(len(data['rows'])):
            bnext_id = int(data['rows'][i][0])+50+int(i)
            bcheck = UserTestScores.query.get(bnext_id)
            while bcheck:
                bnext_id = 100000000 - bnext_id
                bcheck = Movements.query.get(bnext_id)
            reps = UserTestScores(id=bnext_id, user_id=data['rows'][i][1],
                                  move_id=data['rows'][i][2], score=data['rows'][i][4], score_type='reps')

            db.session.add(reps)
            db.session.commit()
            move = Movements.query.get(data['rows'][i][2])
            print(move.name)


def update_score(score):
    if score.score_type == 'reps':
        try:
            score.score = int(score.score) * 5
        except:
            pass
    if score.score_type == 'lbs':
        try:
            score.score = int(score.score) // .60
        except:
            pass
    db.session.commit()


def import_workouts(wod_file, wod_move_file):
    if not wod_file:
        return ' please provide file path'
    if not wod_move_file:
        return ' please provide file path'
    with open(wod_file) as f:
        data = json.load(f)

        for i in range(len(data['rows'])):
            if data['rows'][i][-1] == '0':
                data['rows'][i][-1] = False
            else:
                data['rows'][i][-1] = True
            try:
                wod = Workouts(id=data['rows'][i][0], date=datetime.strptime(
                    data['rows'][i][1][:9], '%Y-%m-%d'))
            except:
                wod = Workouts(id=data['rows'][i][0], date=datetime.strptime(
                    data['rows'][i][1][:10], '%Y-%m-%d'))
            db.session.add(wod)
            db.session.commit()
            component = Components(wod_id=data['rows'][i][0], name=data['rows'][i]
                                   [2], description=data['rows'][i][3], is_benchmark=data['rows'][i][-1])
            db.session.add(component)
            db.session.commit()

    with open(wod_move_file) as f:
        data = json.load(f)
        for i in range(len(data['rows'])):
            comp_move = ComponentMovements(
                component_id=data['rows'][i][1], move_id=data['rows'][i][2])
            db.session.add(comp_move)
            db.session.commit()
