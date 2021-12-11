from flask import request
from flask import render_template
from flask import redirect, url_for
from handlers.authHandlers import getUser
from mongoDB import *

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


def renderPostForm(darkmode):
    return render_template('postForm.html', data={'darkmode': darkmode})


# Gets post data from request object, then saves in mongoDB. Redirects to the created post's page
def createPost(mongoClient, user):
    author = user['username']  #replace with current user ID
    authorID = str(user['_id'])
    #get title and text from form
    title = request.form['title']
    text = request.form['text']

    #get image from form
    image = request.files.get('image', '')

    postObj = {
        "author": author,
        "authorID": authorID,
        "title": title,
        "text": text
    }

    #if user uploaded image, upload to cloudinary
    src = ''
    if image:
        src = uploadImage(image.read())['url']

    postObj['imageUrl'] = src  #add image url to database
    postID = mongoCreatePost(mongoClient, postObj)
    mongoAddPostToUser(mongoClient, postID, authorID)
    return redirect(url_for('renderPost', postID=postID))


# Use postID to retrieve data from database and uploads the postTemplate to show the posts
def getPost(mongoClient, postID):
    user = getUser(request, mongoClient)
    post = mongoGetPost(mongoClient, postID)
    darkmode = getDarkmodeStatus(mongoClient, user['_id'])
    return render_template('postTemplate.html',
                           data={
                               'post': post,
                               'darkmode': darkmode
                           })


def getAllPosts(mongoClient):
    user = getUser(request, mongoClient)
    if user:
        darkmode = getDarkmodeStatus(mongoClient, user['_id'])
        postList = mongoGetAllPosts(mongoClient)
        return render_template('allPosts.html',
                               data={
                                   'postList': postList,
                                   'darkmode': darkmode
                               })
    return redirect(url_for('renderHome'))
