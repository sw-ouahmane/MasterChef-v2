from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)],
                           render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('\nPassword', validators=[DataRequired()],
                             render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()],
                        render_kw={"placeholder": "Title"})
    image_url = StringField('Image URL', validators=[DataRequired()],
                            render_kw={"placeholder": "URL to Image"})
    description = TextAreaField('Description', render_kw={"placeholder": "Description (optional)"})
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()],
                                render_kw={"placeholder": "Ingredients"})
    instructions_url = StringField('Instructions', validators=[DataRequired()],
                                 render_kw={"placeholder": "Url to Instructions"})
    submit = SubmitField('Submit Recipe')
