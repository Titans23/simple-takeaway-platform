from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sql import db
import os

sep = os.sep


class User(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)  # 用户id
    nick_name = db.Column(db.String(32))  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # 密码
    signature = db.Column(db.String(256))  # 个性签名
    gender = db.Column(db.String(8))  # 性别
    orders = db.relationship('Orders', backref='user')
    money = db.Column(db.Integer)
    address = db.Column(db.String(32))
    tel = db.Column(db.String(32))
    # src = db.Column()      # 头像
    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "gender": self.gender if self.gender else "MAN",
            "signature": self.signature if self.signature else ""
        }
        return resp_dict

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Store(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(32), nullable=False)
    key_hash = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128))
    goods = db.relationship("Goods", backref="store")
    money = db.Column(db.Integer)
    orders = db.relationship('Orders', backref='store')
    recommand_good = db.Column(db.Integer)
    collect_p = db.Column(db.Integer)
    sales = db.Column(db.Integer)
    type = db.Column(db.String(32))
    tel = db.Column(db.String(32))
    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "goods": self.goods,
        }
        return resp_dict

    def set_password(self, password):
        self.key_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.key_hash, password)


class Goods(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(32), nullable=False)
    price = db.Column(db.String(8), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey(Store.id))
    sales = db.Column(db.Integer, nullable=False)
    comments = db.relationship('Comments', backref='good')
    detail = db.Column(db.String(128))

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "store_id": self.store_id,
            "sales": self.sales
        }
        return resp_dict


class Riders(db.Model):
    __tablename__ = "riders"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)  # 用户id
    password_hash = db.Column(db.String(128), nullable=False)  # 密码
    orders = db.relationship('Orders', backref='rider')
    money = db.Column(db.Integer)
    tel = db.Column(db.String(32))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Orders(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    price = db.Column(db.String(8), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey(Store.id))
    good_id = db.Column(db.Integer)
    rider_id = db.Column(db.Integer, db.ForeignKey(Riders.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    creat_time = db.Column(db.String(128))
    over_time = db.Column(db.String(128))
    state = db.Column(db.String(64))
    name = db.Column(db.String(64))
    user_address = db.Column(db.String(128))
    store_address = db.Column(db.String(128))
    money = db.Column(db.String(8))
    reward_money = db.Column(db.Integer)
    report_state = db.Column(db.String(32))

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "price": self.price,
            "store_id": self.store_id,
            "good_id": self.good_id,
            "user_id": self.user_id,
            "creat_time": self.creat_time
        }
        return resp_dict


class Comments(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    good_id = db.Column(db.Integer, db.ForeignKey(Goods.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    comment = db.Column(db.String(128))
    nick_name = db.Column(db.String(64))
    judge = db.Column(db.String(32))


class Collect(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey(Store.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))


class Conditions(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    content = db.Column(db.String(64))


# 举报
class Report(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    content = db.Column(db.String(128))
    rider_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    judge = db.Column(db.String(32))
    order_id = db.Column(db.Integer)

# user_id1向user_id2发送请求
class Friend(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer,primary_key=True)
    user_id1 = db.Column(db.String(32), nullable=False)
    user_id2 = db.Column(db.String(32), nullable=False)
    state = db.Column(db.String(32))

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
