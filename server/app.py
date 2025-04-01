#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from werkzeug.security import generate_password_hash
from config import app, db, api
from models import User

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204
    

class Signup(Resource):
    def post(self):
        #Get the data from the request
        data = request.get_json()
        # breakpoint()
        # Check if both usernam and password are provided
        if not data or not data.get('username') or not data.get('password'):
            return {"error": "Username and Password are required."}, 400
        #extract username and password
        username = data.get('username')
        password = data.get('password')
        
        #Check if the username is already taken
        existing_user = User.query.filter(User.username == username).first()
        if existing_user:
            return {"error": "Username already exist."}, 400
        
         #Create a new user instance
        new_user = User(username=username)
        new_user.password_hash = password
        #add the new user to the database and commt
        db.session.add(new_user)
        db.session.commit()

        # Save the user ID in the session
        session['user_id'] = new_user.id
        
        #Return the user object as JSON
        return new_user.to_dict(), 201



class CheckSession(Resource):
    def get(self):
        # Check if the 'user_id' exists in the session
        user_id = session.get('user_id')
        
        if user_id:
            # If user_id exists, fetch the user from the database
            user = db.session.get(User, user_id)
            
            if user:
                # Return the user data in JSON format
                return user.to_dict(), 200
            else:
        
        # If no user is authenticated, return a 204 No Content status
                return {}, 204
        else:
            # If no 'user_id' in session, return 204 No Content
            return {}, 204
        






class Login(Resource):
    def post(self):
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the username and password are provided
        if not data or not data.get('username') or not data.get('password'):
            return {"error": "Username and Password are required."}, 400

        username = data.get('username')
        password = data.get('password')

        # Query the database to find the user by the provided username
        user = User.query.filter(User.username == username).first()

        # If user exists, check if the password is correct
        if user and user.authenticate(password):
            session['user_id'] = user.id  # Store user ID in the session

            # Return user data (excluding the password)
            user_data = user.to_dict()  # Assumes to_dict() method is implemented to serialize the user object
            return user_data, 200

        # If user does not exist or password is incorrect
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        #session.pop('user_id', None) removes the user_id from the session. 
        # If user_id does not exist in the session, it returns None and does nothing.
        session.pop("user_id", None)

        return {}, 204




api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Login, '/login')
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
