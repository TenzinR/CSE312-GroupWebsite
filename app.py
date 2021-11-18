from flask import Flask, request
from flask import abort, redirect, url_for
from flask import render_template
from handlers import *
from mongoDB import Client

# from markupsafe import escape

app = Flask(__name__)

mongoClient = Client()


# home route
@app.route('/')
def renderHome():
    return render_template('index.html')


# log in route
@app.route('/login', methods=['GET', 'POST'])
def routeLogin():
    if request.method == 'GET':
        return renderLoginForm()
    return login(mongoClient)


# register route
@app.route('/register', methods=['GET', 'POST'])
def routeRegister():
    if request.method == 'GET':
        return renderRegisterForm()
    return register(mongoClient)


# create post
@app.route('/posts', methods=['GET', 'POST'])
def routePosts():
    if request.method == 'GET':
        return renderPostForm()
    return createPost(mongoClient)


# go to specific post
@app.route('/posts/<string:postID>')
def renderPost(postID):
    return getPost(mongoClient, postID)


# all chats route
@app.route('/chats/all')
def chatList():
    return render_template('chatIndex.html')


# create chat route
@app.route('/chats', methods=['GET', 'POST'])
def routeChats():
    if request.method == 'GET':
        return renderChatForm()
    return createChat()


# chosen chat route
@app.route('/chats/<int:chatID>')
def renderChat(chatId):
    return getChat(chatId)


# GET, route to list chats - chats/all
# GET, route to render form to create a new chat - /chats
# POST, route to use form data to create new chat - /chats
# GET, route to go to specific chat using id - /chats/<ID>
#
#

# TO-DO List:
# Image upload
# Cookies
# Chats
# Comments
# Flash
# Security