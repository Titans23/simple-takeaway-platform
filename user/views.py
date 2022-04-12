import math
import time
import os
import datetime
import flask_login
from flask_login import logout_user, current_user
from sqlalchemy import and_, or_

from manager import login_manager
from PIL import Image

from user import user_blue
from flask import render_template, request, flash, url_for, redirect, session, current_app
from modules import User, db, Goods, Comments, Store, Collect, Conditions, Orders, Riders, Report, Friend
import random
import hashlib


@login_manager.user_loader
def user_loader(id):
    if not User.query.filter(User.id == id).first():
        return
    user = User.query.filter(User.id == id).first()
    user.id = id
    return user


@user_blue.route('/logout')
@flask_login.login_required
def logout():
    logout_user()
    return redirect('/')


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
    user = User.query.filter(User.id == username).first()
    param = str(username) + str(user.password_hash)
    key = USE_MD5(param)
    if key != get_key:
        return True


# 处理网站logo
@user_blue.route("/favicon.ico")
def get_web_logo():
    return current_app.send_static_file('favicon.ico')


@user_blue.route('/user_login', methods=['GET', 'POST'])
def user_login():
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
                user = User.query.filter(User.id == username).first()
                # 判断数据库中是否存在user
                if user:
                    # 判断密码是否正确
                    if not user.check_password(password):
                        flash("密码错误")
                    else:
                        param = str(username) + str(user.password_hash)
                        key = USE_MD5(param)
                        session['key'] = key
                        flask_login.login_user(user, remember=True, duration=datetime.timedelta(minutes=20))
                        next = request.args.get('next')
                        # print("next",next)
                        return redirect(next or url_for('user.index1'))
                else:
                    flash("该账号不存在")
        # 注册
        elif type2:
            if not all([password, username]):
                flash("请输入完整的账号密码")
            else:
                user = User.query.filter(User.id == username).first()
                # 判断数据库中是否存在user
                if user:
                    flash("该账号已存在")
                else:
                    nick_name = "用户昵称" + str(random.randint(1001, 99999))
                    user = User(id=username, nick_name=nick_name, money=0)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    img_path = './user/user_static/' + str(user.id) + '.png'
                    file1 = open(img_path, 'wb')
                    file2 = open("./user/user_static/first.png", 'rb')
                    file1.write(file2.read())
                    file1.close()
                    file2.close()
                    flash("注册成功")
                    return render_template("user_login.html")

    return render_template("user_login.html")


@user_blue.route('/user/home_id=<int:username>', methods=['GET', 'POST'])
def user_home(username):
    user = User.query.filter(User.id == username).first()
    if request.method == 'POST':
        user.gender = request.form.get('gender')
        user.nick_name = request.form.get('nick_name')
        user.signature = request.form.get('signature')
        user.address = request.form.get('address')
        new_avatar = request.files.get('file')  # 获取图片
        if new_avatar:
            img_path = './user/user_static/' + str(user.id) + '.png'
            img = Image.open(new_avatar)
            img.save(img_path)
        db.session.commit()
    return render_template('user_home.html', user=user)


@user_blue.route('/user/image/<username>', methods=['GET', 'POST'])
def get_image(username):
    image = open(f"./user/user_static/{username}.png", 'rb')
    return image.read()


@user_blue.route('/user/addmoney_id=<int:username>', methods=['POST'])
def addmoney(username):
    if session_judge(username):
        return "非法操作"
    user = User.query.filter(User.id == username).first()
    user.money = user.money + int(request.form.get("add_money"))
    db.session.commit()
    flash('充值成功')
    return render_template('user_home.html', user=user)


@user_blue.route('/user/good_detail/<int:good_id>/<int:username>', methods=['GET'])
def good_detail(good_id, username):
    good = Goods.query.filter(Goods.id == good_id).first()
    user = User.query.filter(User.id == username).first()
    return render_template('detail_good.html', good=good, user=user)


@user_blue.route('/add_comments', methods=['POST'])
def add_comments():
    good_id = request.form.get('good_id')
    username = request.form.get('username')
    comment = request.form.get('comment')
    # print(comment)
    try:
        before_comment = Comments.query.all()[-1]
        before_id = before_comment.id
    except:
        before_id = 0
    id = int(before_id) + 1
    good = Goods.query.filter(Goods.id == good_id).first()
    user = User.query.filter(User.id == username).first()
    # print(user.nick_name)
    comment = Comments(id=id, good_id=good_id, user_id=username, comment=comment, nick_name=user.nick_name,
                       judge="todo")
    db.session.add(comment)
    db.session.commit()
    return render_template('detail_good.html', good=good, user=user)


@user_blue.route('/<int:page>')
def index(page):
    per_page = 6
    paginates = Store.query.order_by('id').paginate(page, per_page, error_out=False)
    stus = paginates.items
    # totalpage为总页面数
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('index.html', paginate=paginates, stus=stus, totalpage=totalpage)


@user_blue.route('/')
def index1():
    return redirect("/1")


@user_blue.route('/collect/store_id=<int:store_id>', methods=['GET', 'POST'])
@flask_login.login_required
def collect_store(store_id):
    if request.method == 'POST':
        try:
            before_collect = Collect.query.all()[-1]
            before_id = before_collect.id
        except:
            before_id = 0
        id = int(before_id) + 1
        user_id = current_user.id
        collect = Collect(id=id, user_id=user_id, store_id=store_id)
        store = Store.query.filter(Store.id == store_id).first()
        store.collect_p = store.collect_p + 1
        db.session.add(collect)
        db.session.commit()
        return redirect(url_for("store.get_store_detail", id=store_id, page=1))


@user_blue.route('/collect', methods=['GET', 'POST'])
@flask_login.login_required
def get_collect_store():
    stores = []
    collects = Collect.query.filter(Collect.user_id == current_user.id).all()
    for collect in collects:
        store = Store.query.filter(Store.id == collect.store_id).first()
        stores.append(store)
    return render_template('user_collect.html', stores=stores)


@user_blue.route('/cancel_collect/store_id=<int:store_id>/type=<type>', methods=['POST'])
@flask_login.login_required
def cancel_collect(store_id, type):
    collect = Collect.query.filter(and_(Collect.user_id == current_user.id, Collect.store_id == store_id)).first()
    db.session.delete(collect)
    store = Store.query.filter(Store.id == store_id).first()
    store.collect_p = store.collect_p - 1
    db.session.commit()
    if type == "home":
        return redirect(url_for("user.get_collect_store"))
    else:
        return redirect(url_for("store.get_store_detail", id=store_id, page=1))


@user_blue.route('/search', methods=['POST'])
def search():
    key_words = str(request.form.get('key_words'))
    # print(key_words)
    search_stores = []
    search_goods = []
    stores = Store.query.filter(Store.id > 0).all()
    goods = Goods.query.filter(Goods.id > 0).all()
    for store in stores:
        if key_words in store.name:
            search_stores.append(store)
    for good in goods:
        if key_words in good.name:
            search_goods.append(good)
    return render_template("user_search.html", goods=search_goods, stores=search_stores, key_words=key_words)


@user_blue.route('/admin/key=admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        comment_id = request.form.get('comment_id')
        comment = Comments.query.filter(Comments.id == comment_id).first()
        if request.form.get('illegal'):
            db.session.delete(comment)
            db.session.commit()
        else:
            comment.judge = "judged"
            db.session.commit()
    tojudge = []
    comments = Comments.query.filter(Comments.judge == "todo").all()
    conditions = Conditions.query.filter(Conditions.id > 0).all()
    for comment in comments:
        for condition in conditions:
            if condition.content in comment.comment:
                tojudge.append(comment)
    return render_template('admin.html', tojudge=tojudge)


@user_blue.route('/admin/key=admin/manage_report?page=<int:page>', methods=['GET'])
def manage_report(page):
    per_page = 10
    paginates = Report.query.filter(or_(Report.judge == "审核中", Report.judge == "骑手申诉")).paginate(page, per_page,
                                                                                                 error_out=False)
    stus = paginates.items
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('admin_manage_report.html', paginate=paginates, stus=stus, totalpage=totalpage)


@user_blue.route('/admin/key=admin/manage_report', methods=["POST"])
def judge_report():
    report_id = request.form.get('report_id')
    report = Report.query.filter(Report.id == report_id).first()
    order_id = report.order_id
    order = Orders.query.filter(Orders.id == order_id).first()
    rider_id = report.rider_id
    rider = Riders.query.filter(Riders.id == rider_id).first()
    if request.form.get('success'):
        order.report_state = "举报成功"
        report.judge = "举报成功"
    else:
        order.report_state = "举报失败"
        report.judge = "举报失败"
        rider.money += 10
    db.session.commit()
    return redirect(url_for("user.manage_report", page=1))


@user_blue.route('/admin/key=admin/change_conditions', methods=['GET', 'POST'])
def change_conditions():
    if request.method == 'POST':
        if request.form.get('delete'):
            condition = Conditions.query.filter(Conditions.id == request.form.get('condition_id')).first()
            db.session.delete(condition)
            db.session.commit()
        else:
            try:
                before_condition = Conditions.query.all()[-1]
                before_id = before_condition.id
            except:
                before_id = 0
            id = int(before_id) + 1
            condition = Conditions(id=id, content=request.form.get('content'))
            db.session.add(condition)
            db.session.commit()
    conditions = Conditions.query.filter(Conditions.id > 0).all()
    return render_template("change_conditions.html", conditions=conditions)


@user_blue.route('/admin/key=admin/search', methods=['GET', 'POST'])
def admin_search():
    state = "null"
    type = "null"
    data = "null"
    if request.method == "POST":
        type = request.form.get('type')
        id = request.form.get('ID')
        if type == "user_id":
            data = User.query.filter(User.id == id).all()
        elif type == "store_id":
            data = Store.query.filter(Store.id == id).all()
        elif type == "rider_id":
            data = Riders.query.filter(Riders.id == id).all()
        elif type == "good_id":
            data = Goods.query.filter(Goods.id == id).all()
        elif type == "order_id":
            data = Orders.query.filter(Orders.id == id).all()
        else:
            data = Report.query.filter(Report.id == id).all()
        if len(data) != 0:
            state = "查询成功"
            data = data[0]
        else:
            state = "查询失败"
    return render_template('admin_search.html', data=data, state=state, type=type)


@user_blue.route('/sort')
def sort_store():
    return render_template('sort.html')


@user_blue.route('/get_sort?type=<type>&page=<int:page>')
def get_sort_store(type, page):
    per_page = 6
    if type == "take_out":
        paginates = Store.query.filter(Store.type == "美食外卖").paginate(page, per_page, error_out=False)
        chinese_type = "美食外卖"
    elif type == "super":
        paginates = Store.query.filter(Store.type == "超市便利").paginate(page, per_page, error_out=False)
        chinese_type = "超市便利"
    elif type == "fruit":
        paginates = Store.query.filter(Store.type == "水果").paginate(page, per_page, error_out=False)
        chinese_type = "水果"
    else:
        paginates = Store.query.filter(Store.type == "甜品饮品").paginate(page, per_page, error_out=False)
        chinese_type = "甜品饮品"
    stus = paginates.items
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('sorted_store.html', paginate=paginates, stus=stus, totalpage=totalpage, type=type,
                           chinese_type=chinese_type)


@user_blue.route('/user_order?page=<int:page>')
@flask_login.login_required
def user_order(page):
    per_page = 10
    paginates = Orders.query.filter(Orders.user_id == current_user.id).paginate(page, per_page, error_out=False)
    stus = paginates.items
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('user_order.html', paginate=paginates, stus=stus, totalpage=totalpage)


@user_blue.route('/user_order/id=<int:order_id>', methods=['POST'])
@flask_login.login_required
def reward_rider(order_id):
    money = request.form.get('money')
    order = Orders.query.filter(Orders.id == order_id).first()
    rider_id = order.rider_id
    rider = Riders.query.filter(Riders.id == rider_id).first()
    user_id = order.user_id
    user = User.query.filter(User.id == user_id).first()
    if user.money >= float(money):
        rider.money += float(money)
        user.money -= float(money)
        order.reward_money = float(money)
        db.session.commit()
        return redirect(url_for("user.user_order", page=1))
    else:
        flash("余额不足请充值")
        return render_template('user_home.html', user=user)


@user_blue.route('/report_rider/id=<int:order_id>', methods=['POST'])
@flask_login.login_required
def report_rider(order_id):
    try:
        before_report = Report.query.all()[-1]
        before_id = before_report.id
    except:
        before_id = 0
    id = int(before_id) + 1
    content = request.form.get('content')
    order = Orders.query.filter(Orders.id == order_id).first()
    order.report_state = "已举报"
    report = Report(content=content, rider_id=order.rider_id, user_id=order.user_id, id=id, order_id=order_id,
                    judge="审核中")
    rider = Riders.query.filter(Riders.id == order.rider_id).first()
    rider.money -= 10
    db.session.add(report)
    db.session.commit()
    return redirect(url_for("user.user_order", page=1))


@user_blue.route('/bind_tel', methods=['POST', 'GET'])
@flask_login.login_required
def bind_tel():
    if request.method == "POST":
        pass
    return render_template('user_bind_tel.html')


@user_blue.route('/search_friend', methods=['POST', 'GET'])
@flask_login.login_required
def search_friend():
    search_ = None
    state = "暂未查询"
    if request.method == "POST":
        username2 = request.form.get('username2')
        user2 = User.query.filter(User.id == username2).first()
        if username2 == current_user.id:
            state = "不能添加自己为好友"
        else:
            if not user2:
                state = "未查询该此人"
            else:
                friend = Friend.query.filter(
                    or_(and_(Friend.user_id1 == username2, Friend.user_id2 == current_user.id),
                        and_(Friend.user_id2 == username2, Friend.user_id1 == current_user.id))).first()
                if friend:
                    if friend.state == "待同意":
                        state = "请勿重复发送申请"
                    else:
                        state = "你们已经是好友"
                else:
                    state = "查询到"
                    search_ = user2
    return render_template('search_friend.html', search_=search_, state=state)


@user_blue.route('/user/apply_friend/user_id2=<user_id2>')
@flask_login.login_required
def apply_friend(user_id2):
    try:
        before_friend = Friend.query.all()[-1]
        before_id = before_friend.id
    except:
        before_id = 0
    id = int(before_id) + 1
    user_id1 = str(current_user.id)
    user_id2 = str(user_id2)
    friend = Friend(user_id1=user_id1, user_id2=user_id2, state="待同意",id=id)
    db.session.add(friend)
    db.session.commit()
    flash("申请已发出")
    return redirect(url_for("user.search_friend"))

@user_blue.route('/user/my_friends')
@flask_login.login_required
def user_friends():
    tofriend = []
    friended = []
    friends = Friend.query.filter(or_(Friend.user_id2 == current_user.id),Friend.user_id1 == current_user.id).all()
    for friend in friends:
        if friend.state == "待同意":
            tofriend.append(friend)
        else:
            friended.append(friend)
    return render_template('user_friends.html',tofriend=tofriend,friended=friended)
