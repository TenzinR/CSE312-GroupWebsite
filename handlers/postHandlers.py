from flask import request
from flask import render_template
from flask import redirect, url_for
from mongoDB import mongoGetPost, mongoCreatePost, mongoGetAllPosts

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
