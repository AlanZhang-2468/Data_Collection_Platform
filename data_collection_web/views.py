from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
import numpy as np
from data_collection_web import app, db
from data_collection_web.models import User, Reaction

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/annotate', methods=['GET', 'POST'])
@login_required
def annotation():
    with open('data.txt', 'r') as f:
        data = f.readlines()
    index = np.random.randint(0, len(data))
    if request.method == 'POST':
        steps = []
        for i in range(1, 1000):  # 假设最多有 1000 个反应步骤
            if 'action{}'.format(i) not in request.form:
                break
            action = request.form['action{}'.format(i)]
            reactant = request.form['reactant{}'.format(i)]
            if action and reactant:
                step = '{} {}'.format(action, reactant)
                steps.append(step)
        steps_str = ' ; '.join(steps)
        reaction = Reaction(text = data[index], steps=steps_str, user_id = current_user.id)
        db.session.add(reaction)
        db.session.commit()
        return redirect(url_for('user_page', username=current_user.username))
    return render_template('annotation.html', data=data[index])

@app.route('/regenerate', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def regenerate():
    return redirect(url_for('annotation'))  # 重定向回主页

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_page(username):
    if current_user.username != username:
        # 如果当前用户不是请求的用户，则重定向到当前用户的页面
        return redirect(url_for('user_page', username=current_user.username))
    user = User.query.filter_by(username=username).first_or_404()
    reaction = Reaction.query.filter_by(user_id=user.id).all()
    reaction_list = [{'reaction_id':r.text.split('.')[0], 'reaction':r} for r in reaction]
    return render_template('user.html', user=user, reaction_list = reaction_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # if len(User.query.all()) != 0:
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        users = User.query.all()
        for user in users:
            # 验证用户名和密码是否一致
            if username == user.username and user.validate_password(password):
                login_user(user)  # 登入用户
                flash('Login success.')
                return redirect(url_for('user_page', username=username))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('home'))  # 重定向回首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('home'))

    return render_template('settings.html')

@app.route('/reaction/edit/<int:reaction_id>', methods=['GET', 'POST'])
@login_required
def edit(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    reaction_steps = reaction.steps.split(' ; ')
    reaction_actions = [step.split(' ')[0] for step in reaction_steps]
    reaction_smiles = [step.split(' ')[1] for step in reaction_steps]
    reaction_text = reaction.text
    
    if request.method == 'POST':
        steps = []
        for i in range(1, 1000):  # 假设最多有 1000 个反应步骤
            if 'action{}'.format(i) not in request.form:
                break
            action = request.form['action{}'.format(i)]
            reactant = request.form['reactant{}'.format(i)]
            if action and reactant:
                step = '{} {}'.format(action, reactant)
                steps.append(step)
        steps_str = ' ; '.join(steps)
        reaction.steps = steps_str
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('edit', reaction_id=reaction_id))
    
    return render_template(
        'edit.html', 
        reaction_text = reaction_text,
        reaction_actions = reaction_actions,
        reaction_smiles = reaction_smiles)  # 传入被编辑的电影记录

@app.route('/reaction/delete/<int:reaction_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)  # 获取电影记录
    db.session.delete(reaction)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('user_page', username=current_user.username))  # 重定向回主页
