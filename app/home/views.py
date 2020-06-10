import random
import string
from functools import wraps

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

from app.models import Goods, Cart, Orders, OrdersDetail
from . import home
from app import db
from .forms import RegisterForm, User, LoginForm
from werkzeug.security import generate_password_hash
from flask import session, redirect, url_for, render_template, make_response, flash, request

"""
生成验证码
"""


def rndColor():
    """随机颜色"""
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def gene_text():
    """生成4位验证码"""
    return ''.join(random.sample(string.ascii_letters + string.digits, 4))


def draw_lines(draw, num, width, height):
    """画线"""
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)


def get_verify_code():
    """生成验证码图形"""
    code = gene_text()
    # 图片大小120*50
    width, hetght = 120, 50
    # 新图片对象
    im = Image.new('RGB', (width, hetght), 'white')
    # 字体
    font = ImageFont.truetype('app/static/fonts/arial.ttf', 40)
    # draw对象
    draw = ImageDraw.Draw(im)
    # 绘制字符串
    for item in range(4):
        draw.text((5 + random.randint(-3, 3) + 23 * item, 5 + random.randint(-3, 3)),
                  text=code[item], fill=rndColor(), font=font)
    return im, code


@home.route('/code')
def get_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str 作为response返回前端,并设置首部自导
    response = make_response(buf_str)
    response.headers["Content-Type"] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response


@home.route("/login/", methods=["GET", "POST"])
def login():
    """登录"""
    if "user_id" in session:  # 如果已经登录,则直接跳转到首页
        return redirect(url_for("home.index"))
    form = LoginForm()  # 实例化LoginForm类
    if form.validate_on_submit():  # 如果提交
        data = form.data  # 接收表单数据
        # 判断用户名和密码是否匹配
        user = User.query.filter_by(username=data["username"]).first()  # 获取用户信息
        if not user:
            flash("用户名不存在!", "error")  # 输入错误信息
            return render_template("home/login.html", form=form)  # 返回登录页
        # 调用check_password()方法,检测用户名密码是否匹配
        if not user.check_password(data["password"]):
            flash("密码错误!", "error")  # 输入错误信息
            return render_template("home/login.html", form=form)  # 返回登录页
        if session.get('image').lower() != form.verify_code.data.lower():
            flash("验证码错误", "error")
            return render_template("home/login.html", form=form)  # 返回登录页
        session["user_id"] = user.id  # 将user_id 写入 session ,后面用于判断用户是否登陆
        session["username"] = user.username  # 将username写入 session ,后面用于判断用户是否登陆
        return redirect(url_for("home.index"))  # 登录成功,跳转到首页
    return render_template('home/login.html', form=form)  # 渲染登陆页面模板


@home.route("/register/", methods=["GET", "POST"])
def register():
    """
        注册功能
    :return:
    """
    form = RegisterForm()  # 实例化RegisterForm类
    if form.validate_on_submit():
        data = form.data  # 接收表单数据
        # 为User类属性赋值
        user = User(
            username=data["username"],  # 用户名
            email=data["email"],
            password=generate_password_hash(data["password"]),  # 对密码进行加密
            phone=data["phone"]
        )
        db.session.add(user)  # 添加数据
        db.session.commit()  # 提交数据
        return redirect(url_for("home.login"))  # 登陆成功
    return render_template("home/register.html", form=form)


@home.route("/logout/")
def logout():
    """
    退出功能
    :return:
    """
    # 重定向到home模块下的登录
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("home.login"))


@home.route("/")
def index():
    """首页"""
    # 获取12个新品
    new_goods = Goods.query.filter_by(is_new=1).order_by(Goods.addtime.desc()).limit(12).all()
    # 获取12个打折商品
    sale_goods = Goods.query.filter_by(is_sale=1).order_by(Goods.addtime.desc()).limit(12).all()
    # 获取2个热门商品
    hot_goods = Goods.query.order_by(Goods.views_count.desc()).limit(2).all()
    return render_template("home/index.html", new_goods=new_goods, sale_goods=sale_goods, hot_goods=hot_goods)  # 渲染模板


@home.route("/goods_detail/<int:id>/")
def goods_detail(id=None):
    """详情页"""
    user_id = session.get('user_id', 0)  # 获取用户ID , 判断用户是否登录
    goods = Goods.query.get_or_404(id)  # 根据商品ID获取商品数据,如果不存在则返回404
    # 浏览量+1
    goods.views_count += 1
    db.session.add(goods)  # 添加数据
    db.session.commit()  # 提交数据
    # 获取左侧热门商品
    hot_goods = Goods.query.filter_by(subcat_id=goods.subcat_id).order_by(Goods.views_count.desc()).limit(5).all()
    # 获取底部相关商品
    similar_goods = Goods.query.filter_by(subcat_id=goods.subcat_id).order_by(Goods.addtime.desc()).limit(5).all()
    return render_template('home/good_detail.html', hot_goods=hot_goods, similar_goods=similar_goods)


def user_login(f):
    """
    登录装饰器
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home.login"))
        return f(*args, **kwargs)

    return decorated_function


@home.route("/cart_add/")
@user_login
def cart_add():
    """
    添加购物车
    :return:
    """
    cart = Cart(
        goods_id=request.args.get('goods_id'),
        number=request.args.get('number'),
        user_id=session.get('user_id', 0)  # 获取用户ID,判断是否登陆
    )
    db.session.add(cart)
    db.session.commit()
    return redirect(url_for('home.shopping_cart'))


@home.route("/shopping_cart/")
@user_login
def shopping_cart():
    """
    查看购物车功能,显示已经添加到购物车中的商品
    :return:
    """
    user_id = session.get('user_id', 0)
    cart = Cart.query.filter_by(user_id=int(user_id)).order_by(Cart.addtime.desc()).all()
    if cart:  # 判断购物车是否存在商品
        return render_template('home/shopping_cart.html')
    else:
        return render_template('home/empty_cart.html')


@home.route("cart_order/", methods=["GET", "POST"])
@user_login
def cart_order():
    """
    保存订单功能
    :return:
    """
    if request.method == "POST":
        user_id = session.get("user_id", 0)  # 获取用户id
        # 添加订单
        orders = Orders(
            user_id=user_id,
            recevie_name=request.form.get('recevie_name'),
            recevie_tel=request.form.get('recevie_tel'),
            recevie_address=request.form.get('recevie_address'),
            remark=request.form.get('remark')
        )
        db.session.add(orders)
        db.session.commit()
        # 添加订单详情
        cart = Cart.query.filter_by(user_id=user_id).all()
        object = []
        for item in cart:
            object.append(OrdersDetail(
                order_id=orders.id,
                goods_id=item.goods_id,
                number=item.number,
            ))
        db.session.add_all(object)
        # 更改购物车状态
        Cart.query.filter_by(user_id=user_id).update({'user_id': 0})
        db.session.commit()
    return redirect(url_for('home.index'))


@home.route("/order_list/", methods=["GET", "POST"])
@user_login
def order_list():
    """
    我的订单
    :return:
    """
    user_id = session.get('user_id', 0)
    orders = OrdersDetail.query.join(Orders).filter(Orders.user_id == user_id).order_by(Orders.addtime.desc()).all()
    return render_template('home/order_list.html', orders=orders)
