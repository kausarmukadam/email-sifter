from flask import Flask
from flask_restful import Resource, Api, reqparse
app = Flask(__name__)
api = Api(app)

# TODO(kausar): Setup flask endpoints. Only public API would be the ask question, reading model metadata is private.
class Model(Resource):
    def askQuestion(self):
        pass


api.add_resource(Model, '/model')