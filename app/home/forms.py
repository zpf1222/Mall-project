# _*_ coding: utf-8 _*_

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, ValidationError, Length
from app.models import User


class RegisterForm(FlaskForm):
    """
    用户注册表单
    """
    username = StringField(
        label="账户:",
        validators=[
            DataRequired("用户名不能为空!"),
            Length(min=3, max=50, message="用户名长度必须在3到50位之间")
        ],
        description="用户名",
        render_kw={
            "type": "text",
            "placeholder": "请输入用户名！",
            "class": "validate-username",
            "size": 38,
        }
    )

    phone = StringField(
        label="联系电话 ：",
        validators=[
            DataRequired("手机号不能为空！"),
            Regexp("1[345789][0-9]{9}", message="手机号码格式不正确")
        ],
        description="手机号",
        render_kw={
            "type": "text",
            "placeholder": "请输入联系电话！",
            "size": 38,
        }
    )

    email = StringField(
        label="邮箱 ：",
        validators=[
            DataRequired("邮箱不能为空！"),
            Email("邮箱格式不正确！")
        ],
        description="邮箱",
        render_kw={
            "type": "email",
            "placeholder": "请输入邮箱！",
            "size": 38,
        }
    )

    repassword = PasswordField(
        label="确认密码 ：",
        validators=[
            DataRequired("请输入确认密码！"),
            EqualTo('password', message="两次密码不一致！")
        ],
        description="确认密码",
        render_kw={
            "placeholder": "请输入确认密码！",
            "size": 38,
        }
    )

    submit = SubmitField(
        '同意协议并注册',
        render_kw={
            "class": "btn btn-primary login",
        }
    )

    def validate_email(self, field):
        """
        检测注册邮箱是否已经存在
        :param field:字段名
        :return:
        """
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("邮箱已经存在!")

    def validate_phone(self, field):
        """
        检测手机号是否存在
        :param field:
        :return:
        """
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("手机号已经存在！")


class LoginForm(FlaskForm):
    """
    登录功能
    """
    username = StringField(
        validators=[
            DataRequired("用户名不能为空!"),
            Length(min=3, max=50, message="用户名长度必须在3到10位之间")
        ],
        description="用户名",
        render_kw={
            "type": "text",
            "placeholder": "请输入用户名！",
            "class": "validate-username",
            "size": 38,
            "maxlength": 99
        }
    )

    password = PasswordField(
        validators=[
            DataRequired("密码不能为空！"),
            Length(min=3, message="密码长度不少于6位")
        ],
        description="密码",
        render_kw={
            "type": "text",
            "placeholder": "请输入密码！",
            "class": "validate-password",
            "size": 38,
            "maxlength": 99
        }
    )
    verify_code = StringField(
        "VerifyCode",
        validators=[DataRequired()],
        render_kw={
            "class": "validate-code",
            "size": 18,
            "maxlength": 4,
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary login",
        }
    )
