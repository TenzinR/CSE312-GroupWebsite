from flask import Flask, request
from flask_socketio import SocketIO, send, emit
from flask import abort, redirect, url_for
from flask import render_template, make_response
from handlers.authHandlers import *
from handlers.chatHandlers import *
from handlers.postHandlers import *
from mongoDB import *
import bcrypt

# from markupsafe import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

mongoClient = Client()


# home route
@app.route('/')
def renderHome():
    token = getToken(request)
    data = ''
    if token:
        user = validateToken(mongoClient, token)
        if user:
            data = user
            addOnlineUser(mongoClient, user)
    else:
        return render_template('landing.html')

    return render_template('index.html', data=data)


# log in route
@app.route('/login', methods=['GET', 'POST'])
def routeLogin():
    if request.method == 'GET':
        return renderLoginForm()

    #login returns 2 things: render_template result, and userID
    [resp, userID] = login(mongoClient)

    if userID:  #if the login credentials were valid
        # take render_template result and wrap it with make_response

        resp = make_response(resp)
        salt = bcrypt.gensalt()
        token = bcrypt.hashpw(userID.encode(), salt)

        #add cookie to response
        resp.set_cookie(key="token", value=token, max_age=3600, httponly=True)

    #use resp instead of render_template when setting cookies
    return resp


# register route
@app.route('/register', methods=['GET', 'POST'])
def routeRegister():
    if request.method == 'GET':
        return renderRegisterForm()
    return register(mongoClient)


@app.route('/logout', methods=['POST'])
def logout():
    user = validateToken(mongoClient, getToken(request))
    removeOnlineUser(mongoClient, user)
    socketio.emit('removeUserFromList', user['username'], broadcast=True)
    resp = make_response(redirect(url_for('renderHome')))
    resp.set_cookie(key='token', value='', max_age=0)  #get rid of cookie
    return resp


# create post
@app.route('/posts', methods=['GET', 'POST'])
def routePosts():
    #we need to get a token to see if the user is logged in
    token = getToken(request)
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


@socketio.on('connect')
def handleConnect():
    token = getToken(request)
    if token:
        user = validateToken(mongoClient, token)
        if user:
            onlineUsers = list(getOnlineUsers(mongoClient))
            if user not in onlineUsers:
                addOnlineUser(mongoClient, user)
            onlyUsernames = []
            for u in onlineUsers:
                onlyUsernames.append(u['username'])
            emit('addUserToList', {'onlyUsernames': onlyUsernames},
                 broadcast=True)


# @socketio.on('windowClose')
# def handleWindowClose():
#     # print("a window was closed")
#     user = validateToken(mongoClient, getToken(request))
#     print(user['username'], ' closed their window')
#     removeOnlineUser(mongoClient, user)
#     emit('removeUserFromList', user['username'], broadcast=True)


@socketio.on('disconnect')
def handleDisconnect():
    user = validateToken(mongoClient, getToken(request))
    print(user['username'], ' closed their window')
    removeOnlineUser(mongoClient, user)
    emit('removeUserFromList', user['username'], broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

# GET, route to list chats - chats/all
# GET, route to render form to create a new chat - /chats
# POST, route to use form data to create new chat - /chats
# GET, route to go to specific chat using id - /chats/<ID>
#

# TO-DO List:
# Cookies -
# Online Users List (websockets)
# Chats (live DMs using websockets)
# Comments - maybe not, might just add upvotes/downvotes
# Flash - messages popping up showing login successful, password requirements not met, etc.
# Security