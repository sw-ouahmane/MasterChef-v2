#!/usr/bin/python3
"""
starts a Flask web application
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegistrationForm, RecipeForm
from werkzeug.security import generate_password_hash, check_password_hash
import api
import random
import json
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '9a04913ab5bb2dfa66bf19ae617b1624'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///masterchef.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
all_recipes = []


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_image_url = db.Column(
        db.String(500), default='static/images/default_profiles.jpg')
    recipes = db.relationship('Recipe', backref='author', lazy=True)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = user = User.query.filter_by(
            email=form.email.data).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))
        else:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully!', 'success')
            return redirect(url_for('logout'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
    if form.email.data and form.password.data:
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def home():
    """returns the index page of the project"""
    global all_recipes
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search = request.form.get('search')
        recipes = None
        if search:
            recipes = api.search_recipes(search, 20)
        return render_template('search_results.html', recipes=recipes, results=search)

    random.shuffle(all_recipes)
    recipes = all_recipes[:3]
    return render_template('home.html', recipes=recipes)


@app.route('/browse', methods=['GET', 'POST'], strict_slashes=False)
def browse():
    """returns the browse page of the project"""
    global all_recipes
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search = request.form.get('search')
        recipes = None
        if search:
            recipes = api.search_recipes(search, 20)
        return render_template('search_results.html', recipes=recipes, results=search)

    random.shuffle(all_recipes)
    return render_template('browse_recipes.html', recipes=all_recipes)


@app.route('/profile')
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('profile.html', user=current_user)


@app.route('/about', methods=['GET', 'POST'], strict_slashes=False)
def about():
    """returns the about page of the project"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search = request.form.get('search')
        recipes = None
        if search:
            recipes = api.search_recipes(search, 20)
        return render_template('search_results.html', recipes=recipes, results=search)
    return render_template('about.html')


@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        new_recipe = Recipe(
            title=form.title.data,
            image_url=form.image_url.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions_url.data,
            user_id=current_user.id
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe submitted successfully!', 'success')
        return redirect(url_for('submit_recipe', form=form))
    return render_template('submit_recipe.html', form=form)


@app.route('/recipe/<int:recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    recipe_data = {
        'title': recipe.title,
        'image_url': recipe.image_url,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions
    }
    return json.dumps(recipe_data)


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You do not have permission to edit this recipe.', 'danger')
        return redirect(url_for('profile'))

    form = RecipeForm()
    if request.method == 'GET':
        form.title.data = recipe.title
        form.image_url.data = recipe.image_url
        form.description.data = recipe.description
        form.ingredients.data = recipe.ingredients
        form.instructions_url.data = recipe.instructions

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.image_url = form.image_url.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions_url.data
        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_recipe.html', form=form, recipe=recipe)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You do not have permission to delete this recipe.', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('profile'))


def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()


def setup_cache():
    global all_recipes
    if not os.path.exists("instance/cache.json"):
        recipes = api.api_cache()
        with open("instance/cache.json", "w") as f:
            f.write(recipes)
        all_recipes = json.loads(recipes)
    else:
        data = None
        with open("instance/cache.json", "r") as f:
            data = f.read()
        all_recipes = json.loads(data)


if __name__ == "__main__":
    create_tables()
    setup_cache()
    app.run(host="0.0.0.0", port="5000")
