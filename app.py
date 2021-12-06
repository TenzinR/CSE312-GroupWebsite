from flask import Flask, request
from flask import abort, redirect, url_for
from flask import render_template, make_response
from pymongo.common import validate
from handlers.authHandlers import *
from handlers.chatHandlers import *
from handlers.postHandlers import *
from mongoDB import Client, validateToken
import bcrypt

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

    #login returns 2 things: render_template result, and userID
    [resp, userID] = login(mongoClient)

    # take render_template result and wrap it with make_response
    resp = make_response(resp)
    salt = bcrypt.gensalt()
    token = bcrypt.hashpw(userID.encode(), salt)
    resp.set_cookie("token", token, 3600, httponly=True)
    return resp


# register route
@app.route('/register', methods=['GET', 'POST'])
def routeRegister():
    if request.method == 'GET':
        return renderRegisterForm()
    return register(mongoClient)


# create post
@app.route('/posts', methods=['GET', 'POST'])
def routePosts():

    token = getToken(
        request)  #we need to get a token to see if the user is logged in

    if token:  # if there is a login cookie, i.e the user is logged in
        #check if token is valid
        if validateToken(mongoClient, token):
            print("logged in!")
            if request.method == 'GET':
                return renderPostForm(
                )  #if GET request, need to display form to create a new post
            return createPost(
                mongoClient)  # if POST request, create post in database

    return redirect(url_for(
        'routeLogin'))  # if token was not found/valid, redirect to login page


@app.route('/posts/all')
def postList():
    return getAllPosts(mongoClient)


# go to specific post
@app.route('/posts/<string:postID>')
def renderPost(postID):
    return getPost(mongoClient, postID)


# create chat route
@app.route('/chats', methods=['GET', 'POST'])
def routeChats():
    if request.method == 'GET':
        return renderChatForm()
    return createChat()


# all chats route
@app.route('/chats/all')
def chatList():
    return render_template('chatIndex.html')


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
# Cookies -
# Online Users List (websockets)
# Chats (live DMs using websockets)
# Comments - maybe not, might just add upvotes/downvotes
# Flash - messages popping up showing login successful, password requirements not met, etc.
# Security