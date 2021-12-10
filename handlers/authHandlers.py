from flask import request
from flask import render_template, flash
from flask import redirect, url_for
from mongoDB import *
import bcrypt

# Bug - when logging in with info not in db, get ValueError


def getToken(request):
    if "token" in request.cookies:
        return request.cookies[
            'token']  #if a user is logged in, there will be a token
    return ""


def getUser(request, mongoClient):
    token = getToken(request)
    #checks if there is a token (userid) associated with the cookie
    if token:
        return validateToken(mongoClient, token)
    return False


def getDarkmodeToken(request):
    if 'darkmode' in request.cookies:
        return request.cookies['darkmode']
    return ''


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
    # print("dbUser: ", dbUser)
    if dbUser:  #if user was found in database, log them in
        # print(str(dbUser["_id"]))
        return str(dbUser['_id'])
    return ''  #user not found, so render login form again


# Renders the registerForm page
def renderRegisterForm():
    return render_template('registerForm.html')


# Registers user, saving their data in mongoDB
def register(mongoClient):
    userObj = createUserObj(request)

    #send user to DB
    if not usernameTaken(mongoClient, userObj):
        if passwordRequirements(userObj['password']):
            registerUser(mongoClient, userObj)
            return redirect(url_for('renderHome'))
        print('Password does not meet requirements!')
    else:
        print('Username taken!')
    return redirect(url_for('routeRegister'))


def passwordRequirements(password):
    # print("password: ", password)
    passwordLen = len(password)
    lowercaseCount = 0
    uppercaseCount = 0
    numberCount = 0
    specialCount = 0
    for c in password:
        if not c.isalnum():
            specialCount += 1
        if c.isupper():
            uppercaseCount += 1
        if c.islower():
            lowercaseCount += 1
        if c.isnumeric():
            numberCount += 1
    # print("lowercaseCount: ", lowercaseCount)
    # print("uppercaseCount: ", uppercaseCount)
    # print("numberCount: ", numberCount)
    # print("specialCount: ", specialCount)
    # print("spaceCount: ", spaceCount)
    # print("len: ", passwordLen)

    if passwordLen < 8 or lowercaseCount == 0 or uppercaseCount == 0 or numberCount == 0 or specialCount == 0:
        return False
    return True
