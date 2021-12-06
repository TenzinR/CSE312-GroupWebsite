from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for
from mongoDB import mongoGetPost, registerUser, loginUser, mongoCreatePost, mongoGetAllPosts


def getToken(request):
    token = ""
    if "token" in request.cookies:
        token = request.cookies[
            'token']  #if a user is logged in, there will be a token
    return token


# Create an object that holds the current user's username and password
def createUserObj(request):
    username = request.form['username']
    password = request.form['password']
    userObj = {'username': username, 'password': password}
    return userObj


# Renders loginForm page to login
def renderLoginForm():
    return render_template('loginForm.html')


# Checks if login is correct or not and redirects accordingly
def login(mongoClient):
    userObj = createUserObj(request)
    dbUser = loginUser(mongoClient, userObj)
    if dbUser:
        print(str(dbUser["_id"]))
        return redirect(url_for('renderHome')), str(dbUser['_id'])
    return renderLoginForm()


# Renders the registerForm page
def renderRegisterForm():
    return render_template('registerForm.html')


# Registers user, saving their data in mongoDB
def register(mongoClient):
    userObj = createUserObj(request)

    #send user to DB
    if registerUser(mongoClient, userObj):
        return redirect(url_for('renderHome'))
    return redirect(url_for('routeRegister'))