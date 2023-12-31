import os
import sys
import click
import numpy as np
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

WIN = sys.platform.startswith('win')
if WIN:  
    prefix = 'sqlite:///'
else:  
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id): 
    user = User.query.get(int(user_id)) 
    return user  # 返回用户对象

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) 
    password_hash = db.Column(db.String(128)) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Reaction(db.Model):
    __tablename__ = 'reaction'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), nullable=False)
    steps = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', primaryjoin='Reaction.user_id == User.id')


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
        for i in range(1, 1000):
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

@app.route('/regenerate', methods=['POST'])
@login_required
def regenerate():
    return redirect(url_for('annotation'))

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_page(username):
    if current_user.username != username:
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
            if username == user.username and user.validate_password(password):
                login_user(user) 
                flash('Login success.')
                return redirect(url_for('user_page', username=username))

        flash('Invalid username or password.') 
        return redirect(url_for('login'))

    return render_template('login.html')

@app.cli.command() 
@click.option('--drop', is_flag=True, help='Create after drop.') 
def initdb(drop):
    """Initialize the database."""
    if drop:  
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') 

@app.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Goodbye.')
    return redirect(url_for('home')) 

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
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
        for i in range(1, 1000): 
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
        reaction_smiles = reaction_smiles)

@app.route('/reaction/delete/<int:reaction_id>', methods=['POST'])  
@login_required
def delete(reaction_id):
    reaction = Reaction.query.get_or_404(reaction_id)
    db.session.delete(reaction) 
    db.session.commit() 
    flash('Item deleted.')
    return redirect(url_for('user_page', username=current_user.username))


