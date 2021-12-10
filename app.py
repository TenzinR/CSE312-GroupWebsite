from flask import Flask, request
from flask_socketio import SocketIO, send, emit
from flask import abort, redirect, url_for
from flask import render_template, make_response
from handlers.authHandlers import *
from handlers.chatHandlers import *
from handlers.postHandlers import *
from mongoDB import *
import bcrypt
import secrets

# from markupsafe import escape

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16).encode()
socketio = SocketIO(app)

mongoClient = Client()

# home route
"""renderHome Function Summary:
    This functions purpose is to send user to either landing.html (for the user to 
    register and login) or to the home page. Essentially remembers logins with the
    usage of cookie tokens
"""


@app.route('/')
def renderHome():
    #sets token equal to a user id (a cookie which can contain a users id)
    user = getUser(request, mongoClient)
    if user:
        addOnlineUser(mongoClient, user)
        darkmode = getDarkmodeStatus(mongoClient, user['_id'])

    else:
        return render_template('landing.html')
    return render_template('index.html',
                           data={
                               'user': user,
                               'darkmode': darkmode
                           })


# log in route
@app.route('/login', methods=['GET', 'POST'])
def routeLogin():
    resp = make_response(renderLoginForm())
    if request.method == 'GET':
        return resp

    #login returns userID
    userID = login(mongoClient)

    if userID:  #if the login credentials were valid
        #respond with the user's account page

        resp = redirect(url_for('routeUser', userID=userID))
        salt = bcrypt.gensalt()
        token = bcrypt.hashpw(userID.encode(), salt)

        #add cookie to response
        resp.set_cookie(key="token", value=token, max_age=3600, httponly=True)

    #use resp instead of render_template when setting cookies
    return resp


@app.route('/user/<string:userID>')
def routeUser(userID):
    user = getUser(request, mongoClient)
    username = user['username']
    if userID == str(user['_id']):
        userPosts = mongoGetUserPosts(mongoClient, userID)
        darkmode = getDarkmodeStatus(mongoClient, userID)
        return render_template('accountTemplate.html',
                               data={
                                   'userPosts': userPosts,
                                   'darkmode': darkmode,
                                   'username': username
                               })
    return redirect(url_for('renderHome'))


# register route
@app.route('/register', methods=['GET', 'POST'])
def routeRegister():
    if request.method == 'GET':
        return renderRegisterForm()
    return register(mongoClient)


@app.route('/logout', methods=['POST'])
def logout():
    user = getUser(request, mongoClient)
    removeOnlineUser(mongoClient, user)
    socketio.emit('removeUserFromList', user['username'], broadcast=True)
    resp = make_response(redirect(url_for('renderHome')))
    resp.set_cookie(key='token', value='', max_age=0)  #get rid of cookie
    return resp


# create post
@app.route('/posts', methods=['GET', 'POST'])
def routePosts():
    #we need to get a token to see if the user is logged in
    user = getUser(request, mongoClient)
    if user:
        if request.method == 'GET':
            #if GET request, need to display form to create a new post
            darkmode = getDarkmodeStatus(mongoClient, user['_id'])
            return renderPostForm(darkmode)
        return createPost(mongoClient,
                          user)  # if POST request, create post in database

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


@app.route('/darkmode')
def routeDarkmode():
    token = getToken(request)
    user = validateToken(mongoClient, token)
    toggleDarkmode(mongoClient, user['_id'])
    return redirect(url_for('routeUser', userID=str(user['_id'])))


@app.route('/socketgame')
def routeSocketGame():
    user = getUser(request, mongoClient)
    if user:
        darkmode = getDarkmodeStatus(mongoClient, user['_id'])
        addOnlineUser(mongoClient, user)
        return render_template('socketGame.html',
                               data={
                                   'user': user,
                                   'darkmode': darkmode
                               })
    return redirect(url_for('routeLogin'))


@socketio.on('connect')
def handleConnect():
    user = getUser(request, mongoClient)
    if user:
        onlineUsers = list(getOnlineUsers(mongoClient))
        if user not in onlineUsers:
            addOnlineUser(mongoClient, user)
        onlyUsernames = []
        for u in onlineUsers:
            onlyUsernames.append(u['username'])
        emit('addUserToList', {'onlyUsernames': onlyUsernames}, broadcast=True)


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
    removeOnlineUser(mongoClient, user)
    emit('removeUserFromList', user['username'], broadcast=True)


@socketio.on('serverIncrement')
def handleIncrement(currentCount):
    newCount = int(currentCount) + 1
    emit('clientIncrement', newCount, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

# GET, route to list chats - chats/all
# GET, route to render form to create a new chat - /chats
# POST, route to use form data to create new chat - /chats
# GET, route to go to specific chat using id - /chats/<ID>
#

# TO-DO List:
# Authentication for every page that needs it - before rendering socketGame, check if user logged in
# Darkmode across every page
# DM's with notifications
# go over/finish security