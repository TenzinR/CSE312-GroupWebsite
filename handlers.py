from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for

# store username and password
users = {}
# store recipient and message
chats = []


def renderLoginForm():
    return render_template('loginForm.html')


def login():
    if request.form['username'] in users:
        if users[request.form['username']] == request.form['password']:
            return redirect(url_for('renderHome'))
    return renderLoginForm()


def renderRegisterForm():
    return render_template('registerForm.html')


def register():
    users[request.form['username']] = request.form['password']
    return redirect(url_for('renderHome'))


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
