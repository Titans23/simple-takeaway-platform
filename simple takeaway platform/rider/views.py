import math
import time

from rider import rider_blue
from flask import render_template, request, flash, url_for, redirect, session,current_app
from modules import User, db, Goods,Riders, Orders
import random
import hashlib
# md5加密
def USE_MD5(test):
    if not isinstance(test, bytes):
        test = bytes(test, 'utf-8')
    m = hashlib.md5()
    m.update(test)
    return m.hexdigest()
# 判断用户是否正常访问登录
def session_judge(username):
    get_key = session.get('key')
    rider = Riders.query.filter(Riders.id == username).first()
    param = str(username) + str(rider.password)
    key = USE_MD5(param)
    if key != get_key:
        return True

# 处理网站logo
@rider_blue.route("/favicon.ico")
def get_web_logo():
    return current_app.send_static_file('favicon.ico')


@rider_blue.route('/rider_login', methods=['GET', 'POST'])
def rider_login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        type1 = request.form.get('login')
        type2 = request.form.get('register')
        # 登录类型
        if type1:
            if not all([password, username]):
                flash("请输入完整的账号密码")
            else:
                rider = Riders.query.filter(Riders.id == username).first()
                # 判断数据库中是否存在user
                if rider:
                    # 判断密码是否正确
                    if rider.password != password:
                        flash("密码错误")
                    else:
                        param = str(username)+str(password)
                        key = USE_MD5(param)
                        session['key'] = key
                        return redirect(f"/rider/home_id={username}")
                else:
                    flash("该账号不存在")
        # 注册
        elif type2:
            if not all([password, username]):
                flash("请输入完整的账号密码")
            else:
                rider = Riders.query.filter(Riders.id == username).first()
                # 判断数据库中是否存在user
                if rider:
                    flash("该账号已存在")
                else:
                    rider = Riders(id=username,password=password,money=0)
                    db.session.add(rider)
                    db.session.commit()
                    flash("注册成功")
                    return render_template("rider_login.html")

    return render_template("rider_login.html")

@rider_blue.route('/rider/home_id=<int:username>',methods=['GET','POST'])
def rider_home(username):
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        rider_id = request.form.get('rider_id')
        order = Orders.query.filter(Orders.id == order_id).first()
        order.state = "骑手已送达"
        order.over_time = time.strftime("%H:%M:%S", time.localtime())
        rider = Riders.query.filter(Riders.id == username).first()
        rider.money = rider.money + float(order.money)
        db.session.commit()
    rider = Riders.query.filter(Riders.id == username).first()
    if session_judge(username):
        return "非法操作"
    return render_template('rider_home.html',rider=rider)

@rider_blue.route('/rider/get_orders/<int:id>/<int:page>',methods=['GET','POST'])
def get_orders(id,page):
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        order = Orders.query.filter(Orders.id == order_id).first()
        order.rider_id = id
        order.state = '骑手已接手'
        db.session.commit()
    rider = Riders.query.filter(Riders.id == id).first()
    # orders = Orders.query.filter(Orders.state == '商家已接手').all()
    # print(id,page)
    if not page:
        page = 1
    # 从数据库查询数据
    paginates = Orders.query.filter(Orders.state == '商家已接手').paginate(page, 3, error_out=False)
    stus = paginates.items
    # totalpage为总页面数
    totalpage = math.ceil(paginates.total / 2)
    return render_template('get_orders.html', paginate=paginates, stus=stus, totalpage=totalpage,rider=rider)


    # return render_template('get_orders.html',orders=orders,rider=rider)




