from flask import Flask, request
from flask import render_template
from flask import abort, redirect, url_for
from mongoDB import mongoGetPost, registerUser, loginUser, mongoCreatePost, mongoGetAllPosts
# from werkzeug.utils import secure_filename

# store recipient and message
chats = []

# IMAGE_CACHE = '/images'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv


def uploadImage(img):
    load_dotenv()

    cloudinary.config(cloud_name=os.getenv('CLOUD_NAME'),
                      api_key=os.getenv('API_KEY'),
                      api_secret=os.getenv('API_SECRET'))
    result = cloudinary.uploader.upload(img)
    return result


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
    if dbUser:
        print(str(dbUser["_id"]))
        return redirect(url_for('renderHome')), str(dbUser['_id'])
    return renderLoginForm()


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


# Renders the postForm page
def renderPostForm():
    return render_template('postForm.html')


# Gets post data from request object, then saves in mongoDB. Redirects to the created post's page
def createPost(mongoClient):
    author = 'Bob'  #replace with current user ID

    #get title and text from form
    title = request.form['title']
    text = request.form['text']

    #get image from form
    image = request.files.get('image', '')
    print("title: ", title)
    print("text: ", text)
    print("image: ", image)

    postObj = {"author": author, "title": title, "text": text}

    #if user uploaded image, upload to cloudinary
    src = ''
    if image:
        src = uploadImage(image.read())['url']
        print(src)

    postObj['imageUrl'] = src  #add image url to database
    postID = mongoCreatePost(mongoClient, postObj)
    return redirect(url_for('renderPost', postID=postID))


# Use postID to retrieve data from database and uploads the postTemplate to show the posts
def getPost(mongoClient, postID):
    post = mongoGetPost(mongoClient, postID)
    print(post)
    return render_template('postTemplate.html', data=post)


def getAllPosts(mongoClient):
    postList = mongoGetAllPosts(mongoClient)
    return render_template('allPosts.html', data=postList)


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
