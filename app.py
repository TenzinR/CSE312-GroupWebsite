from flask import Flask, request
from flask import abort, redirect, url_for
from flask import render_template
from handlers import *
from mongoDB import Client
# from markupsafe import escape

app = Flask(__name__)

client = Client()


# home route
@app.route('/')
def renderHome():
    return render_template('index.html')


# log in route
@app.route('/login', methods=['GET', 'POST'])
def routeLogin():
    if request.method == 'GET':
        return renderLoginForm()
    return login(client)


# register route
@app.route('/register', methods=['GET', 'POST'])
def routeRegister():
    if request.method == 'GET':
        return renderRegisterForm()
    return register(client)


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
@app.route('/chats/<int:chatId>')
def renderChat(chatId):
    return getChat(chatId)


# GET, route to list chats - chats/all
# GET, route to render form to create a new chat - /chats
# POST, route to use form data to create new chat - /chats
# GET, route to go to specific chat using id - /chats/<ID>
#
#

# TO-DO List:
# specific subreddit route - reddit.com/r/<subreddit>
# view all subreddits route - reddit.com/subreddits
# create subreddit route - reddit.com/subreddits/create
# list all chatrooms - reddit.com/chats/
# chatroom route - reddit.com/chats/<chatroomID>
# create post route - reddit.com/r/<subreddit>/new - renders form page to make a new post, can only post to an existing subreddit