from flask import Blueprint

store_blue = Blueprint("store", __name__, static_folder='store_static', template_folder='store_templates')

# 导入视图函数
from store import views
