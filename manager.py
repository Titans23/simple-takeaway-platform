from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# 配置信息
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/info'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "west2online"

app.config.from_object(Config)

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

from store import store_blue
from user import user_blue
from rider import rider_blue
app.register_blueprint(user_blue)
app.register_blueprint(store_blue)
app.register_blueprint(rider_blue)
if __name__ == '__main__':
    app.run()
