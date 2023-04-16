import pickle
from flask import Flask, render_template, request
app = Flask(__name__)


crop_predictor = pickle.load(open('crop_predictor.pkl', 'rb'))
crop_yield_predictor = pickle.load(open('yield_predictor.pkl', 'rb'))
fertilizer_predictor = pickle.load(open('fertilizer_predictor.pkl', 'rb'))

@app.route('/')
def index():
    return render_template('index.html')

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
        crop = prediction[0]

        print(crop)
        return render_template('crop_recommendation.html', crop=crop)

    return render_template('crop_recommendation.html')


@app.route('/crop-yield-predict', methods=['GET', 'POST'])
def crop_yield_predict():
    if request.method == 'POST':
        crop = request.form.get('crop')
        year = (int)(request.form.get('year'))
        rainfall = (int)(request.form.get('rainfall'))
        pesticides = (int)(request.form.get('pesticides'))
        temperature = (float)(request.form.get('temperature'))

        prediction = crop_yield_predictor.predict([[crop, year, rainfall, pesticides, temperature]])

        print(prediction[0])
        return render_template('crop_yield_prediction.html', Yield=prediction[0])

    return render_template('crop_yield_prediction.html')

@app.route('/fertilizer-predict', methods=['GET', 'POST'])
def fertilizer_predict():
    if request.method == 'POST':
        nitrogen = request.form.get('nitrogen')
        phosphorus = request.form.get('phosphorus')
        potassium = request.form.get('potassium')
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        moisture = request.form.get('moisture')
        soil = request.form.get('soil')
        crop = request.form.get('crop')

        print(crop)

        prediction = fertilizer_predictor.predict(
            [[temperature, humidity, moisture, soil, crop, nitrogen, potassium, phosphorus]]
        )
        fertilizer = prediction[0]

        print(fertilizer)
        return render_template('fertilizer_prediction.html', fertilizer=fertilizer)

    return render_template('fertilizer_prediction.html')


if __name__ == '__main__':
    app.run(debug=True)
