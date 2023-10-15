#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204
api.add_resource(ClearSession, '/clear')
class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

api.add_resource(IndexArticle, '/articles')
class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())
            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ShowArticle, '/articles/<int:id>')

class Login(Resource):
    def post(self):
        # Get username from JSON request
        username = request.get_json()["username"]

        # Match to db
        user = db.session.query(User).filter_by(username=username).first()

        # check if user exists
        if not user:
            return {"message": "User not found"}, 404

        session["user_id"] = user.id
        return user.to_dict(), 200

api.add_resource(Login, "/login")

class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {"message": "204: No Content"}, 204

api.add_resource(Logout, "/logout")

class CheckSession(Resource):
    def get(self):
        # Retrieve session's user by user id
        user = db.session.query(User).filter(User.id == session.get("user_id")).first()
        if not user:
            return {}, 401
        else:
            return user.to_dict(), 200

api.add_resource(CheckSession, "/check_session")
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
