from flask import Flask
from sql import db
from flask_login import LoginManager
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
app = Flask(__name__)


# 配置信息
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/info'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "west2online"


app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/user_login'


from store import store_blue
from user import user_blue
from rider import rider_blue

app.register_blueprint(user_blue)
app.register_blueprint(store_blue)
app.register_blueprint(rider_blue)
manager = Manager(app)
migrate = Migrate(app,db)

manager.add_command('db', MigrateCommand)
if __name__ == '__main__':
    manager.run()
