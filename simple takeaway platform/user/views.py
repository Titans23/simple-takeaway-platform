import math
import time
import os

from PIL import Image

from user import user_blue
from flask import render_template, request, flash, url_for, redirect, session,current_app
from modules import User, db, Goods, Comments
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
    user = User.query.filter(User.id == username).first()
    param = str(username) + str(user.password)
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
                    if user.password != password:
                        flash("密码错误")
                    else:
                        param = str(username)+str(password)
                        key = USE_MD5(param)
                        session['key'] = key
                        return redirect(f"/user/home_id={username}")
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
                    nick_name = "用户昵称"+str(random.randint(1001,99999))
                    user = User(id=username,password=password,nick_name=nick_name,money=0)
                    db.session.add(user)
                    db.session.commit()
                    flash("注册成功")
                    return render_template("user_login.html")

    return render_template("user_login.html")

@user_blue.route('/user/home_id=<int:username>',methods=['GET','POST'])
def user_home(username):
    user = User.query.filter(User.id == username).first()
    img_path = './user/user_static/' + str(user.id) + '.png'
    user_img = os.path.exists(img_path)
    if not user_img:
        file1 = open(img_path, 'wb')
        file2 = open("./user/user_static/first.png", 'rb')
        file1.write(file2.read())
        file1.close()
        file2.close()
    if request.method == 'POST':
        user.gender = request.form.get('gender')
        user.nick_name = request.form.get('nick_name')
        user.signature = request.form.get('signature')
        user.address = request.form.get('address')
        new_avatar = request.files['file']   # 获取图片
        if new_avatar:
            img = Image.open(new_avatar)
            img.save(img_path)
        db.session.commit()
    if session_judge(username):
        return "非法操作"
    return render_template('user_home.html',user=user)
@user_blue.route('/user/image/<int:username>',methods=['GET','POST'])
def get_image(username):
    image = open(f"./user/user_static/{username}.png", 'rb')
    return image.read()

@user_blue.route('/user/order_id=<int:username>/<int:page>',methods=['GET','POST'])
def user_order(username,page):
    if session_judge(username):
        return "非法操作"
    per_page = 3
    paginates = Goods.query.order_by('id').paginate(page, per_page, error_out=False)
    stus = paginates.items
    # totalpage为总页面数
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('user_order.html',username=username,paginate = paginates,stus = stus,totalpage = totalpage)

@user_blue.route('/user/addmoney_id=<int:username>',methods=['POST'])
def addmoney(username):
    if session_judge(username):
        return "非法操作"
    user = User.query.filter(User.id == username).first()
    user.money = user.money + int(request.form.get("add_money"))
    db.session.commit()
    flash('充值成功')
    return render_template('user_home.html',user=user)

@user_blue.route('/user/good_detail/<int:good_id>/<int:username>',methods=['GET'])
def good_detail(good_id,username):
    good = Goods.query.filter(Goods.id == good_id).first()
    user = User.query.filter(User.id == username).first()
    return render_template('detail_good.html',good=good,user=user)

@user_blue.route('/add_comments',methods=['POST'])
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
    print(user.nick_name)
    comment = Comments(id=id, good_id=good_id, user_id=username, comment=comment,nick_name=user.nick_name)
    db.session.add(comment)
    db.session.commit()
    return render_template('detail_good.html',good=good,user=user)













