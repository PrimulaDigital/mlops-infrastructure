import json
import os
import joblib
import pandas as pd
from flask import Flask, request

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return json.dumps({'message': 'Pong!'})

@app.route('/invocations', methods=['POST'])
def predict():
    model_path = os.path.join('/opt/ml/model', 'model.joblib')
    model = joblib.load(model_path)

    data = request.get_json(force=True)
    input_df = pd.DataFrame(data['instances'])

    predictions = model.predict(input_df).tolist()
    return json.dumps({'predictions': predictions})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
