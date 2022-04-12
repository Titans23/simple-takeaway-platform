import json
import os
import re
import time
import random
import urllib.parse

import flask_login
import requests
from PIL import Image
from flask_login import current_user
from sqlalchemy import and_
import math
from store import store_blue
from flask import render_template, request, flash, url_for, redirect, session, current_app,jsonify
from modules import User, db, Store, Goods, Orders ,Collect
from user.views import USE_MD5

# 判断商家是否正常访问登录
def session_judge(username):
    get_key = session.get('key')
    store = Store.query.filter(Store.id == username).first()
    param = str(username) + str(store.key_hash)
    key = USE_MD5(param)
    if key != get_key:
        return True


@store_blue.route('/store',methods=['GET'])
def get_store():
    request_data = request.get_json()
    page = int(request_data.get('page',1))
    per_page = int(request_data.get('per_page',2))
    if not all([page,per_page]):
        return jsonify(code=404,msg='参数不齐全')
    data = []
    paginates = Store.query.order_by('id').paginate(page, per_page, error_out=False).items
    for paginate in paginates:
        paginate = paginate.to_dict()
        data.append(paginate)
    return jsonify(code=200,msg='OK',data=data)

@store_blue.route('/store',methods=['POST'])
def register_store():
    my_json = request.get_json()
    id = my_json.get('id')
    name = my_json.get('name')
    key = my_json.get('key')
    if not all([id,name,key]):
        return jsonify(code=400,msg='参数不齐全')
    store = Store.query.filter(Store.id == id).first()
    if store:
        return jsonify(code=400,msg='该id已经存在')
    else:
        store = Store(id=id,name=name)
        store.set_password(key)
        db.session.add(store)
        db.session.commit()
        return jsonify(code=200,msg='OK')
@store_blue.route('/goods',methods=['GET','POST'])
def goods():
    # 增加商品
    if request.method == "POST":
        my_json = request.get_data()
        data = urllib.parse.unquote(my_json)
        # 查询数据库中最后一个商品的id 然后在此基础上+1
        try:
            before_good = Goods.query.all()[-1]
            before_id = before_good.id
        except:
            before_id = 0
        id = int(before_id)+1
        pattern = re.compile(r'.*?=(?P<detail>.*?)&name=(?P<name>.*?)&price=(?P<price>.*?)&store_id=',re.S)
        result = re.finditer(pattern, data)
        # print(data)
        for it in result:
            # detail = it.group('detail')
            detail = it.group('detail')
            name = it.group('name')
            price = it.group('price')
            store_id = data[-1]
            sales = 0
            if not all([name,price,store_id]):
                return jsonify(code=400,msg="参数不齐全")
            good = Goods(id=id,name=name,price=price,store_id=store_id,sales=sales,detail=detail)
            db.session.add(good)
            db.session.commit()
            return jsonify(code=200,msg='OK')
    request_data = request.args
    # print(request_data)
    page = int(request_data.get('page',1))
    per_page = int(request_data.get('per_page',2))
    if not all([page, per_page]):
        return jsonify(code=404, msg='参数不齐全')
    data = []
    paginates = Goods.query.order_by('id').paginate(page, per_page, error_out=False).items
    for paginate in paginates:
        paginate = paginate.to_dict()
        data.append(paginate)
    # print(data)
    return jsonify(code=200, msg='OK', data=data)
@store_blue.route('/order',methods=['GET','POST'])
def order():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name',"error")
        price = request.form.get('price')
        store_id = request.form.get('store_id')
        # print(username,name,price,store_id)
        user = User.query.filter(User.id == username).first()
        if float(user.money) < float(price):
            flash('余额不足请充值')
            return render_template('user_home.html',user=user)
        good = Goods.query.filter(and_(Goods.name == name,Store.id == store_id)).first()
        store = Store.query.filter(Store.id == store_id).first()
        # print(name,price,store_id)
        # 查询数据库中最后一个订单的id 然后在此基础上+1
        try:
            before_order = Orders.query.all()[-1]
            before_id = before_order.id
        except:
            before_id = 0
        id = int(before_id) + 1
        order = Orders(id=id,price=price,store_id=store_id,user_id=user.id,state="未接手",creat_time=time.strftime("%H:%M:%S", time.localtime()),good_id=good.id,name=good.name,user_address=user.address,store_address=store.address,money=float(price)*0.1)
        # 用户点餐，扣钱，商家加钱
        user.money = user.money - float(price)
        store.money = store.money + float(price)*0.8
        good.sales += 1
        store.sales += 1
        db.session.add(order)
        db.session.commit()
        return redirect(url_for("user.user_order",page=1))
@store_blue.route('/store_login', methods=['GET', 'POST'])
def store_login():
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
                store = Store.query.filter(Store.id == username).first()
                # 判断数据库中是否存在user
                if store:
                    # 判断密码是否正确
                    if not store.check_password(password):
                        flash("密码错误")
                    else:
                        param = str(username)+str(store.key_hash)
                        key = USE_MD5(param)
                        session['key'] = key
                        return redirect(f"/store/home_id={username}")
                else:
                    flash("该账号不存在")
        # 注册
        elif type2:
            if not all([password, username]):
                flash("请输入完整的账号密码")
            else:
                store = Store.query.filter(Store.id == username).first()
                # 判断数据库中是否存在user
                if store:
                    flash("该商家账号已存在")
                else:
                    name = "店铺名称"+str(random.randint(1001,99999))
                    store = Store(id=username,money=0,name=name,collect_p=0,sales=0,type="美食外卖")
                    store.set_password(password)
                    db.session.add(store)
                    db.session.commit()
                    flash("注册成功")
                    img_path = './store/store_pic/' + str(username) + '.png'
                    file1 = open(img_path, 'wb')
                    file2 = open("./store/store_pic/first.png", 'rb')
                    file1.write(file2.read())
                    file1.close()
                    file2.close()
                    return render_template("store_login.html")
    return render_template("store_login.html")

@store_blue.route('/store/home_id=<int:username>',methods=['GET','POST'])
def store_home(username):
    store = Store.query.filter(Store.id == username).first()
    if request.method == 'POST':  # 获取图片
        if request.form.get('name'):
            store.name = request.form.get('name')
            store.address = request.form.get('address')
            new_avatar = request.files.get('file')
            store.type = request.form.get('type')
            if new_avatar:
                img = Image.open(new_avatar)
                img_path = './store/store_pic/' + str(username) + '.png'
                img.save(img_path)
            db.session.commit()
        if request.form.get('order_id'):
            order = Orders.query.filter(Orders.id == request.form.get('order_id')).first()
            order.state = '商家已接手'
            db.session.commit()
            return redirect(url_for("store.store_orders",store_id=order.store_id,page=1))
    if session_judge(username):
        return "非法操作"
    return render_template('store_home.html',store=store)
@store_blue.route('/store/manage_goods/<int:id>',methods=['GET','POST'])
def manage_goods(id):
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.files.get('file')    # 获取图片
        detail = request.form.get('detail')
        # print(image)
        try:
            before_good = Goods.query.all()[-1]
            before_id = before_good.id
        except:
            before_id = 0
        new_id = int(before_id) + 1
        img_path = './store/store_static/' + str(new_id) + '.png'
        if image:
            img = Image.open(image)
            img.save(img_path)

        data = {
            "detail" : detail,
            "name": name,
            "price": price,
            "store_id": id,
        }
        requests.post('http://127.0.0.1:5000/goods',data=data)
        return redirect(f'/store/manage_goods/{id}')
    store = Store.query.filter(Store.id == id).first()
    recommand_good = Goods.query.filter(Goods.id == store.recommand_good).first()
    return render_template('store_manage.html',store=store,recommand_good=recommand_good)
@store_blue.route('/store/store_orders/store_id=<int:store_id>&<int:page>')
def store_orders(store_id,page):
    per_page = 10
    store = Store.query.filter(Store.id == store_id).first()
    paginates = Orders.query.order_by('creat_time').paginate(page, per_page, error_out=False)
    stus = paginates.items
    totalpage = math.ceil(paginates.total / per_page)
    return render_template('store_orders.html',paginate = paginates,stus = stus,totalpage = totalpage,store=store)
@store_blue.route('/store/delete_good/<int:id>',methods=['POST'])
def delete_good(id):
    if request.method == 'POST':
        if request.form.get('delete'):
            good = Goods.query.filter(Goods.id == id).first()
            store_id = good.store_id
            Goods.query.filter(Goods.id == id).delete()
            db.session.commit()
        else:
            good = Goods.query.filter(Goods.id == id).first()
            store_id = good.store_id
            store = Store.query.filter(Store.id == store_id).first()
            store.recommand_good = good.id
            db.session.commit()
    return redirect(f'/store/manage_goods/{store_id}')

@store_blue.route('/store/manage_goods/image/<username>',methods=['GET','POST'])
def get_image(username):
    image = open(f"./store/store_static/{username}.png", 'rb')
    return image.read()

@store_blue.route('/store/get_pic/<int:username>',methods=['GET','POST'])
def get_pic(username):
    image = open(f"./store/store_pic/{username}.png", 'rb')
    return image.read()

@store_blue.route("/store?id=<int:id>&&page=<int:page>")
@flask_login.login_required
def get_store_detail(id,page):
    per_page = 6
    store = Store.query.filter(Store.id == id).first()
    paginates = Goods.query.filter(Goods.store_id == store.id).paginate(page, per_page, error_out=False)
    stus = paginates.items
    totalpage = math.ceil(paginates.total / per_page)
    try:
        current_user_id = current_user.id
    except:
        current_user_id = None
    collect = Collect.query.filter(and_(Collect.user_id == current_user_id,Collect.store_id == store.id)).first()
    if store.recommand_good:
        recommand_good = Goods.query.filter(Goods.id == store.recommand_good).first()
    else:
        recommand_good = None
    return render_template('store.html',paginate = paginates,stus = stus,totalpage = totalpage,id=id,store=store,collect=collect,recommand_good=recommand_good)










