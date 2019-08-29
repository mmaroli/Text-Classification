from flask import Flask, request, jsonify
from scripts.predict import Predictor


app = Flask(__name__)
classifier = Predictor()

# curl -i -H "Content-Type: application/json" -X POST -d '{"text": "TEXT GOES HERE"}' http://127.0.0.1:5000/ad-category/api/v1.0/classifier
# resp = requests.post(url='http://127.0.0.1:5000/ad-category/api/v1.0/classifier', json={'text': 'Hello World'})
@app.route('/ad-category/api/v1.0/classifier', methods=['POST'])
def classify():
    data = request.json['text']
    response = classifier.classify(text=data)
    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
