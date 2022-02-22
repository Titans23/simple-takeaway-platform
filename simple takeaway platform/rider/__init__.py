from flask import Blueprint

rider_blue = Blueprint("rider",__name__,static_folder='rider_static',template_folder='rider_templates')

# 导入视图函数
from rider import views
