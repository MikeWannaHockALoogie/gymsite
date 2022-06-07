import json
from operator import truediv
from sys import argv
import secrets
import os
import random
from PIL import Image
from flask import url_for
from flask_app.models import Movements, UserWorkouts, Users, UserTestScores, ComponentMovements, Components, Workouts
from flask_app import db, mail, app
from flask_mail import Message
from flask_bcrypt import generate_password_hash
from datetime import datetime, timedelta



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
        "Password Reset Request", sender="renegadeathleticscft@gmail.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password visit the following string:
{url_for("reset_password", token = token, _external = True)}

If you did not submit this request ignore this email and no changes will be made.
"""
    mail.send(msg)


def pick_movements()->list:
    full = random.choice(Movements.query.filter(Movements.full == True).all())
    total = random.choice(Movements.query.filter(Movements.total == True).all())
    push = random.choice(Movements.query.filter(Movements.push == True).all())
    pull = random.choice(Movements.query.filter(Movements.pull == True).all())
    upper = random.choice(Movements.query.filter(Movements.upper == True).all())
    lower = random.choice(Movements.query.filter(Movements.lower == True).all())
    moves = [full,total,lower,upper,push,pull]
    
    for move in moves:
        if moves.count(move)>1:
            new_move = random.choice(Movements.query.all())
            moves.remove(move)
            moves.append(new_move)
    return moves

def write_test(move):
    if move.kind =='Weightlifting':
        option = random.choice(['AMRAP', 'Interval','Max'])
        if option == 'AMRAP':
            return f'5min AMRAP \n{move}'
        elif option =='Interval':
            return f'30sec on 30 sec off\n{move}'
        else:
            return f'5rep Max\n{move}'
    else:
        option = random.choice(['AMRAP', 'Interval'])
        if option == 'AMRAP':
            return f'5min AMRAP \n{move}'
        else:
            return f'30sec on 30 sec off\n{move}'

def progression_writer(moves,num_weeks=5)->dict:
    progression = dict()
    for i in range(num_weeks):
        progression[f'Week {i}'] = dict()
        for move in moves:
            progression[f'Week {i}'][move]=''
    for move in progression['Week 0']:
        progression['Week 0'][move] = write_test(move)
    for week in range(1,num_weeks):
        for move in progression[f'Week {week}']:
            progression[f'Week {week}'][move] = random.choice([
                f'3 x 2M AMRAP 1 min rest \n{move}',
                f'EMOM x 7 min \n{move}',
                f'EMOM Until fail + 1 ea round\n{move}',
                f'3 x Max Reps\n{move}',
                f'5 Rounds add weight\n{move}'
            ])
    return progression

def workout_writer(progression)->dict:
    global_movements = Movements.query.all()
    count = 1
    workouts= dict()
    yesterday=[]
    for week in progression.keys():
        for day in progression[week]:
            part_a = [progression[week][day],[day]]
            cdm = random.choice(Movements.query.filter(Movements.kind==day.kind).all())
            cool_down = [f'for time complete\n{cdm}',[cdm]]
            moves = [day,cool_down]
            workout = []
            if cool_down == None:
                num_moves = random.choice([2,3,3,4])
            else:
                num_moves = random.choice([1,2,2,3])
            for i in range(num_moves):
                move = None
                kind = []
                while move == None:
                    move = random.choice(global_movements)
                    if move in moves:
                        move = None
                    elif move.kind in kind:
                        move = None
                    elif move in yesterday:
                        move = None
                    else:
                        workout.append(move)
                        moves.append(move)
                        kind.append(move.kind)
            yesterday=moves
            title = ''
            if len(workout) ==1:
                if workout[0].kind == 'Weightlifting':
                    title = random.choice([f'{i}-{i}-{i}-{i}-{i}' for i in range(1,6)] )
                elif workout[0].kind == 'Gymnastics':
                    title = random.choice(['Death By',f'{random.randint(12,31)}M max Reps',f'EMOM for {random.randint(8,15)}'])
                else:
                    title = random.choice(['10 rounds rest 1x', '20 Min max', '5 x 3 min on 1min off'])
            else:
                title =random.choice([f'AMRAP {random.randint(10,20)} Minutes', f'{random.randint(3,7)} RFT' ])
            m = '\n'
            workouts[count] = {'part_a':part_a,'part_b':[f'{title}{m.join([str(wod)for wod in workout])}',workout],'part_c':cool_down}
            count +=1

    return workouts

def assign_components(wod_id:int, components:list, name,description,score_type,is_test=False,is_benchmark = False):
    comp = Components(wod_id = wod_id,name= name,description = description,is_test=is_test,is_benchmark= is_benchmark,score_type=score_type)
    db.session.add(comp)
    db.session.commit()
    if type(components) != list:
        print(components, ' not a list')
    for move in components:
        print(type(move), move)
        m = ComponentMovements(move_id = move.id,component_id = comp.id)
        db.session.add(m)
        db.session.commit()



def assign_workout(ath,workouts):
    date = datetime.today()
    for workout in workouts:
        wod = Workouts(date= date)
        db.session.add(wod)
        db.session.commit()
        user_wod = UserWorkouts(wod_id=wod.id, user_id=int(ath))
        db.session.add(user_wod)
        db.session.commit()
        for part in workouts[workout]:
            if int(workout)<=6:
                if part == 'part_a':
                    if '30sec' or 'AMRAP' in workouts[workout][part][0]:
                        score_type = 'reps'
                    else:
                        score_type = 'lbs'
                    assign_components(
                        wod_id=int(wod.id),
                        components=workouts[workout][part][-1],
                        name = part,
                        description = workouts[workout][part][0],
                        score_type=score_type,
                        is_test = True
                        )
                else:
                    if 'AMRAP' or 'EMOM' or 'min' in workouts[workout][part][0]:
                        score_type ='reps'
                    elif 'RFT' in workouts[workout][part][0]:
                        score_type = 'time'
                    else:
                        score_type = 'lbs'
                    assign_components(
                            wod_id=int(wod.id),
                            components=workouts[workout][part][-1],
                            name = part,
                            description = workouts[workout][part][0],
                            score_type=score_type,
                            )
            else:
                if 'AMRAP' or 'EMOM' or 'min' in workouts[workout][part][0]:
                    score_type ='reps'
                elif 'RFT' in workouts[workout][part][0]:
                    score_type = 'time'
                else:
                    score_type = 'lbs'
                assign_components(
                        wod_id=int(wod.id),
                        components=workouts[workout][part][-1],
                        name = part,
                        description = workouts[workout][part][0],
                        score_type=score_type,
                        )
        date +=timedelta(days =1)


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
