# import datetime
#
# from flask import Flask, jsonify
# from google.auth import jwt
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def login():
#     app.config['SECRET_KEY'] = 'ccf07ef2cb3c4233ae412249e4c13baa'
#     token = jwt.encode({'user': 'asdfvxcvb', 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
#                        app.config['SECRET_KEY'])
#     return jsonify({'token': token.decode('UTF-8')})
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000)
