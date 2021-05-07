from flask_app import db, login_manager, encrypt, app
from flask_bcrypt import generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_sqlalchemy import Model
from flask_login import UserMixin
from datetime import date, datetime
import json


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, default="default.jpeg")
    is_admin = db.Column(db.Boolean, default=False)
    score = db.relationship("GeneralScores", backref="general_scores", lazy=True)
    movement_scores = db.relationship(
        "UserTestScores", backref="movement_scores", lazy=True
    )
    benchmark_scores = db.relationship(
        "BenchmarkScores", backref="benchmark_scores", lazy=True
    )
    workouts = db.relationship("UserWorkouts", backref="wods", lazy=True)

    def __repr__(self):
        return f"{self.name}"

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_seconds)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return Users.query.get(user_id)


class Workouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=date.today().strftime("%b-%d-%Y"))
    components = db.relationship("Components", backref="components", lazy=True)
    user = db.relationship("UserWorkouts", backref="user", lazy=True)

    def __repr__(self):
        return f"{self.date}"


class UserWorkouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wod_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        user = Users.query.get(self.user_id)
        wod = Workouts.query.get(self.wod_id)
        return f"{user.username}, {wod}"


class Components(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wod_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_test = db.Column(db.Boolean, default=False)
    is_benchmark = db.Column(db.Boolean, default=False)
    movements = db.relationship("ComponentMovements", backref="movements", lazy=True)
    score = db.relationship("GeneralScores", backref="component_scores", lazy=True)
    score_type = db.Column(db.String)

    def __repr__(self):
        return f"{self.description}"


class Movements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    upper = db.Column(db.Boolean, default=False, nullable=False)
    lower = db.Column(db.Boolean, default=False, nullable=False)
    full = db.Column(db.Boolean, default=False, nullable=False)
    push = db.Column(db.Boolean, default=False, nullable=False)
    pull = db.Column(db.Boolean, default=False, nullable=False)
    total = db.Column(db.Boolean, default=False, nullable=False)
    kind = db.Column(db.String(), nullable=False)
    components = db.relationship("ComponentMovements", backref="components", lazy=True)
    movement_scores = db.relationship(
        "UserTestScores", backref="user_test_scores", lazy=True
    )

    def __repr__(self):
        return f"{self.name}"


class ComponentMovements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    move_id = db.Column(db.Integer, db.ForeignKey("movements.id"), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)

    def __repr__(self):
        movement = Movements.query.get(self.move_id)
        componenet = Components.query.get(self.component_id)
        return f"{movement}"


class GeneralScores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer)
    score_type = db.Column(db.String)
    notes = db.Column(db.String)


class UserTestScores(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    move_id = db.Column(db.Integer, db.ForeignKey("movements.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer)
    score_type = db.Column(db.String)
    test_day = db.Column(db.Date)
    notes = db.Column(db.String)


class BenchmarkScores(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer)
    score_type = db.Column(db.String)
    notes = db.Column(db.String)


def score_import(file):
    if not file:
        return " please provide file path"
    with open(file) as f:
        data = json.load(f)

        for i in range(len(data["rows"])):
            anext_id = int(data["rows"][i][0])
            acheck = UserTestScores.query.get(anext_id)
            while acheck:
                anext_id += 51
                acheck = Movements.query.get(anext_id)

            load = UserTestScores(
                id=anext_id,
                user_id=data["rows"][i][1],
                move_id=data["rows"][i][2],
                score=data["rows"][i][3],
                score_type="lbs",
            )

            db.session.add(load)
            db.session.commit()
            move = Movements.query.get(data["rows"][i][2])
            user = Users.query.get(data["rows"][i][1])
            print(user.username, move.name, load.score, load.score_type)

        for i in range(len(data["rows"])):
            bnext_id = int(data["rows"][i][0]) + 50 + int(i)
            bcheck = UserTestScores.query.get(bnext_id)
            while bcheck:
                bnext_id = 100000000 - bnext_id
                bcheck = Movements.query.get(bnext_id)
            reps = UserTestScores(
                id=bnext_id,
                user_id=data["rows"][i][1],
                move_id=data["rows"][i][2],
                score=data["rows"][i][4],
                score_type="reps",
            )

            db.session.add(reps)
            db.session.commit()
            move = Movements.query.get(data["rows"][i][2])
            user = Users.query.get(data["rows"][i][1])
            print(user.username, move.name, reps.score, reps.score_type)


def update_score(score):
    if score.score_type == "reps":
        try:
            score.score = int(score.score) * 5
        except:
            pass
    if score.score_type == "lbs":
        try:
            score.score = int(score.score) // 0.60
        except:
            pass
    db.session.commit()


def import_workouts(wod_file, wod_move_file):
    if not wod_file:
        return " please provide file path"
    if not wod_move_file:
        return " please provide file path"
    with open(wod_file) as f:
        data = json.load(f)

        for i in range(len(data["rows"])):
            if data["rows"][i][-1] == "0":
                data["rows"][i][-1] = False
            else:
                data["rows"][i][-1] = True
            try:
                wod = Workouts(
                    id=data["rows"][i][0],
                    date=datetime.strptime(data["rows"][i][1][:9], "%Y-%m-%d"),
                )
            except:
                wod = Workouts(
                    id=data["rows"][i][0],
                    date=datetime.strptime(data["rows"][i][1][:10], "%Y-%m-%d"),
                )
            db.session.add(wod)
            db.session.commit()
            component = Components(
                wod_id=data["rows"][i][0],
                name=data["rows"][i][2],
                description=data["rows"][i][3],
                is_benchmark=data["rows"][i][-1],
            )
            db.session.add(component)
            db.session.commit()

    with open(wod_move_file) as f:
        data = json.load(f)
        for i in range(len(data["rows"])):
            comp_move = ComponentMovements(
                component_id=data["rows"][i][1], move_id=data["rows"][i][2]
            )
            db.session.add(comp_move)
            db.session.commit()


def delete_workouts():
    for workout in Workouts.query.all():
        for comp in workout.components:
            for score in GeneralScores.query.all():
                if score.component_id == comp.id:
                    db.session.delete(score)
            for bmscore in BenchmarkScores.query.all():
                if score.component_id == comp.id:
                    db.session.delete(bmscore)
            for item in ComponentMovements.query.all():
                if item.component_id == comp.id:
                    db.session.delete(item)
            db.session.delete(comp)
        db.session.delete(workout)
    db.session.commit()
