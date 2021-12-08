from flask import request
from flask import render_template
from flask import redirect, url_for
from mongoDB import registerUser, loginUser
import bcrypt

# Bug - when logging in with info not in db, get ValueError


def getToken(request):
    if "token" in request.cookies:
        return request.cookies[
            'token']  #if a user is logged in, there will be a token
    return ""


def getDarkmodeToken(request):
    if 'darkmode' in request.cookies:
        return request.cookies['darkmode']
    return 'false'


def validateDarkmode(darkmodeToken):
    try:
        return bcrypt.checkpw('true'.encode(), darkmodeToken.encode())
    except:
        return False


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
    if registerUser(mongoClient, userObj):
        return redirect(url_for('renderHome'))
    return redirect(url_for('routeRegister'))
