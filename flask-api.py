from flask import Flask, jsonify, request
from http import HTTPStatus  # includes different http statuses
import books
from books import books
from phonecodes import phone_codes_array
import json
app = Flask(__name__) #creates Flask class instance
import pandas as pd
import random

with open('area-code.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

@app.route('/')
def index():
    return 'Index Page'   #just leave it here.
@app.route('/state', methods = ['GET'])
def get_state_name():
     # if key doesn't exist, returns a 400, bad request error
    code = request.args['code']
    numOfCities = len(data[str(code)])
    if numOfCities > 1:
        return jsonify(data[str(code)][random.randint(0, numOfCities -1 )])
    return jsonify(data[str(code)])
@app.route('/codes', methods = ['GET'])
def get_city_name():
     # if key doesn't exist, returns a 400, bad request error
    code = request.args['code']
    numOfCities = len(data[str(code)])
    if numOfCities > 1:
        return jsonify(data[str(code)][random.randint(0, numOfCities -1 )])
    return jsonify(data[str(code)])



if __name__ == '__main__': #starts the flask server
     app.run()
