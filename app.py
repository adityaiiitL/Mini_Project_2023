import pickle
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'


crop_predictor = pickle.load(open('crop_predictor.pkl', 'rb'))
crop_yield_predictor = pickle.load(open('yield_predictor.pkl', 'rb'))
fertilizer_predictor = pickle.load(open('fertilizer_predictor.pkl', 'rb'))


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists, please choose different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                raise ValidationError("Wrong Password")
        else:
            raise ValidationError("User not found")
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/crop-recommend', methods=['GET', 'POST'])
def crop_predict():
    # if request.method == 'POST':
    #     nitrogen = request.form.get('nitrogen')
    #     phosphorus = request.form.get('phosphorus')
    #     potassium = request.form.get('potassium')
    #     temperature = request.form.get('temperature')
    #     humidity = request.form.get('humidity')
    #     ph = request.form.get('ph')
    #     rainfall = request.form.get('rainfall')

    #     prediction = crop_predictor.predict(
    #         [[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]]
    #     )
    #     crop = prediction[0]

    #     print(crop)
    #     return render_template('crop_recommendation.html', crop=crop)

    return render_template('crop_recommendation.html')


@app.route('/crop-yield-predict', methods=['GET', 'POST'])
def crop_yield_predict():
    # if request.method == 'POST':
    #     crop = request.form.get('crop')
    #     year = (int)(request.form.get('year'))
    #     rainfall = (int)(request.form.get('rainfall'))
    #     pesticides = (int)(request.form.get('pesticides'))
    #     temperature = (float)(request.form.get('temperature'))

    #     prediction = crop_yield_predictor.predict([[crop, year, rainfall, pesticides, temperature]])

    #     print(prediction[0])
    #     return render_template('crop_yield_prediction.html', Yield=prediction[0])

    return render_template('crop_yield_prediction.html')


@app.route('/fertilizer-predict', methods=['GET', 'POST'])
def fertilizer_predict():
    # if request.method == 'POST':
    #     nitrogen = request.form.get('nitrogen')
    #     phosphorus = request.form.get('phosphorus')
    #     potassium = request.form.get('potassium')
    #     temperature = request.form.get('temperature')
    #     humidity = request.form.get('humidity')
    #     moisture = request.form.get('moisture')
    #     soil = request.form.get('soil')
    #     crop = request.form.get('crop')

    #     print(crop)

    #     prediction = fertilizer_predictor.predict(
    #         [[temperature, humidity, moisture, soil, crop, nitrogen, potassium, phosphorus]]
    #     )
    #     fertilizer = prediction[0]

    #     print(fertilizer)
    #     return render_template('fertilizer_prediction.html', fertilizer=fertilizer)

    return render_template('fertilizer_prediction.html')


if __name__ == '__main__':
    app.run(debug=True)
