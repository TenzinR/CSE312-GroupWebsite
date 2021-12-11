from flask import Flask, request, redirect, url_for, render_template, flash
from flask_socketio import SocketIO, emit
from handlers.authHandlers import *
from handlers.postHandlers import *
from mongoDB import *
import bcrypt
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16).encode()
socketio = SocketIO(app)
leastCount = 0

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
    if request.method == 'GET':
        return render_template('loginForm.html')

    #login returns userID
    userID = login(mongoClient)

    if userID:  #if the login credentials were valid
        #respond with the user's account page
        #use resp instead of render_template when setting cookies

        resp = redirect(url_for('renderHome'))
        salt = bcrypt.gensalt()
        token = bcrypt.hashpw(userID.encode(), salt)

        #add cookie to response
        resp.set_cookie(key="token", value=token, max_age=3600, httponly=True)
        return resp
    else:
        flash('Login failed! Please review your credentials.')
        return redirect(url_for('routeLogin'))


@app.route('/user/<string:userID>')
def routeUser(userID):
    user = getUser(request, mongoClient)
    if user:
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
        flash("You are not authorized to view that user's page!")
        return redirect(url_for('renderHome'))
    flash('You are not logged in!')
    return redirect(url_for('routeLogin'))


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
    resp = redirect(url_for('renderHome'))
    resp.set_cookie(key='token', value='', max_age=0,
                    httponly=True)  #get rid of cookie
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
        emit('countRequest', broadcast=True)
        emit('addUserToList', {'onlyUsernames': onlyUsernames}, broadcast=True)


@socketio.on('serverMessage')
def handleMessage(messageObj):
    print(messageObj)
    recipientUsername = messageObj['recipientUsername']
    senderUsername = messageObj['senderUsername']
    messageText = messageObj['messageText']
    emit('clientMessage', {
        'senderUsername': senderUsername,
        'recipientUsername': recipientUsername,
        'messageText': messageText
    },
         broadcast=True)


@socketio.on('disconnect')
def handleDisconnect():
    user = getUser(request, mongoClient)
    removeOnlineUser(mongoClient, user)
    emit('removeUserFromList', user['username'], broadcast=True)


@socketio.on('serverIncrement')
def handleIncrement(currentCount):
    newCount = int(currentCount) + 1
    emit('clientIncrement', newCount, broadcast=True)


@socketio.on('countResponse')
def compareResponse(clientCount):
    global leastCount
    print('leastCount: ' + str(leastCount) + ' clientCount: ', clientCount)
    if int(clientCount) > leastCount:
        leastCount = int(clientCount)
        emit('clientIncrement', clientCount, broadcast=True)
    elif int(clientCount) == 0:
        emit('clientIncrement', leastCount, broadcast=True)


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