import iss 

from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])

def index():
	return render_template('index.html')

app.run(host='0.0.0.0', debug=True)
