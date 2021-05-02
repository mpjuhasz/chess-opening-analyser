from flask import Flask, request
from flask_restful import Api, Resource
import argparse
from chess_com_hook import User
# from openings_tree_builder import OTB
from graph_handling import GraphBuilder


app = Flask('NextMove')
api = Api(app)


class GetHandler(Resource):
    @staticmethod
    def get():
        return 'TASTES GOOD STILL'

api.add_resource(GetHandler, "/get")
api.add_resource(User, "/post")
# api.add_resource(OTB, "/openings/get")
api.add_resource(GraphBuilder, "/openings/get")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--prod', action='store_true')

if parser.parse_args().prod:
    app.run(host='0.0.0.0', debug=False, port=8888, ssl_context=('/root/www/certificate.pem', '/root/www/key.pem'))
else:
    app.run(host='0.0.0.0', debug=False, port=5000)


if __name__ == '__main__':
    print('this is needed...')