from flask import Blueprint

user_blue = Blueprint("user",__name__,static_folder='user_static',template_folder='user_templates')

# 导入视图函数
from user import views

