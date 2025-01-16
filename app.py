from flask import Flask,jsonify,request,render_template,send_file
from flask_cors import CORS
from utils import connect_database
import logging as logger
logger.basicConfig(level="DEBUG")
from routes import api_bp
import os
app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return render_template('home.html')


# Enregistrer le blueprint API
app.register_blueprint(api_bp, url_prefix='/api')


# initialisation
if __name__ == '__main__':
    #from waitress import serve
    #serve(app, host='192.168.1.124', port=5000)
    app.run(host="0.0.0.0", port=os.environ.get('PORT_NUMBER'),debug=True)
    app.run(debug=True)


    