from flask import Flask
from flask_restful import Resource, Api, reqparse
app = Flask(__name__)
api = Api(app)

# TODO: Setup public API for asking question, other eval functions like reading model metadata are private.
class Model(Resource):
    def askQuestion(self):
        pass

api.add_resource(Model, '/model')