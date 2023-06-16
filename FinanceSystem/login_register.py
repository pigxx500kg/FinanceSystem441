from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/finance_news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 配置 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# 定义 User 模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))


# 创建一个应用上下文并创建所有的数据库表
with app.app_context():
    db.create_all()


# 定义登陆表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    login = SubmitField('登录')
    register = SubmitField('注册')


# 定义用户加载函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 定义登陆视图
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if form.login.data:
            # 登陆操作
            if user is None or user.password != form.password.data:
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        elif form.register.data:
            # 注册操作
            if user is not None:
                flash('Username already exists')
                return redirect(url_for('login'))
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login_register.html', form=form)
