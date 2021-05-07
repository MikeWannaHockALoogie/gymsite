from flask_app import app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# init database migrations
migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
