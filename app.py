import pickle
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder='templates', static_folder='css')
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
        min=4, max=20)], render_kw={"placeholder": "Andrew"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": ""})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists, please choose different one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Andrew"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": ""})

    submit = SubmitField("Login")


# @app.route('/')
# def home():
#     return render_template('home.html')


@app.route('/', methods=['GET', 'POST'])
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


crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 'mothbeans',
         'mungbean', 'blackgram', 'lentil', 'pomegranate', 'banana', 'mango', 'grapes',
         'watermelon', 'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'cotton',
         'jute', 'coffee']
encoded_crops_type = [20, 11, 3, 9, 18, 13, 14, 2,
                      10, 19, 1, 12, 7, 21, 15, 0, 16, 17, 4, 6, 8, 5]


@app.route('/crop-recommend', methods=['GET', 'POST'])
def crop_predict():
    if request.method == 'POST':
        nitrogen = request.form.get('nitrogen')
        phosphorus = request.form.get('phosphorus')
        potassium = request.form.get('potassium')
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        ph = request.form.get('ph')
        rainfall = request.form.get('rainfall')

        prediction = crop_predictor.predict(
            [[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]]
        )

        for i in range(22):
            if encoded_crops_type[i] == prediction[0]:
                crop = crops[i]
                break

        print(crop)

        print(nitrogen)
        return render_template('crop_recommendation.html', crop=crop)

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


soil_type = ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey']
encoded_soil_type = [4, 2, 0, 3, 1]
crop_type = ['Maize', 'Sugarcane', 'Cotton', 'Tobacco', 'Paddy',
             'Barley', 'Wheat', 'Millets', 'Oil seeds', 'Pulses', 'Ground Nuts']
encoded_crop_type = [3, 8, 1, 9, 6, 0, 10, 4, 5, 7, 2]
fertilizer_type = ['Urea', 'DAP', '14-35-14',
                   '28-28', '17-17-17', '20-20', '10-26-26']
encoded_fertilizer_type = [6, 5, 1, 4, 2, 3, 0]


@app.route('/fertilizer-predict', methods=['GET', 'POST'])
def fertilizer_predict():
    if request.method == 'POST':
        nitrogen = request.form.get('nitrogen')
        phosphorus = request.form.get('phosphorus')
        potassium = request.form.get('potassium')
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        moisture = request.form.get('moisture')
        soil = str(request.form.get('soil_select'))
        crop = str(request.form.get('crop_select'))

        print(soil)
        for i in range(5):
            if soil_type[i] == soil:
                encoded_s = encoded_soil_type[i]
                break

        for i in range(11):
            if crop_type[i] == crop:
                encoded_c = encoded_crop_type[i]
                break

        prediction = fertilizer_predictor.predict(
            [[temperature, humidity, moisture, encoded_s,
                encoded_c, nitrogen, potassium, phosphorus]]
        )
        for i in range(7):
            if prediction[0] == encoded_fertilizer_type[i]:
                fertilizer = fertilizer_type[i]
                break

        return render_template('fertilizer_prediction.html', fertilizer=fertilizer)

    return render_template('fertilizer_prediction.html')


if __name__ == '__main__':
    app.run(debug=True)
