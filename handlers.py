from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for
from mongoDB import registerUser, loginUser

# store username and password
users = {}
# store recipient and message
chats = []


def createUserObj(request):
    username = request.form['username']
    password = request.form['password']
    userObj = {'username': username, 'password': password}
    return userObj


def renderLoginForm():
    return render_template('loginForm.html')


def login(client):
    userObj = createUserObj(request)
    if loginUser(client, userObj):
        return redirect(url_for('renderHome'))
    return renderLoginForm()


def renderRegisterForm():
    return render_template('registerForm.html')


def register(client):
    userObj = createUserObj(request)
    if registerUser(client, userObj):
        return redirect(url_for('renderHome'))
    return redirect(url_for('routeRegister'))


def renderChatForm():
    return render_template('chatForm.html')


def createChat():
    recipient = request.form['recipient']
    message = request.form['message']
    chats.append([recipient, message])
    return redirect(url_for('renderChat', chatId=len(chats) - 1))


def getChat(chatId):
    recipient = chats[chatId][0]
    message = chats[chatId][1]
    return "Recipient: {}".format(recipient) + "\r\n Message: {}".format(
        message)
