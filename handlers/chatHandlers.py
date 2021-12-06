from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for

chats = []


# Render the chatForm page
def renderChatForm():
    return render_template('chatForm.html')


#
def createChat():
    recipient = request.form['recipient']
    message = request.form['message']
    chats.append([recipient, message])
    return redirect(url_for('renderChat', chatID=len(chats) - 1))


#
def getChat(chatID):
    recipient = chats[chatID][0]
    message = chats[chatID][1]
    return "Recipient: {}".format(recipient) + "\r\n Message: {}".format(
        message)
