from pymongo import MongoClient
from bson.objectid import ObjectId


class Client:
    def __init__(self):

        self.client = MongoClient("localhost", 27017)
        print("MONGO CONNECTION OPEN!")
        self.db = self.client.reddit_clone
        self.user_collection = self.db.user_collection
        self.chat_collection = self.db.chat_collection
        self.post_collection = self.db.post_collection


#
def registerUser(mongoClient, user):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    #TO-DO: check if username exists
    usernameTaken = mongoClient.user_collection.find_one(
        {"username": user['username']})
    if usernameTaken:
        print("Registration Failed")
        return False  #need to add something to show user on client side that username is taken
    mongoClient.user_collection.insert_one(user)
    print("Registration Successful!")
    return True


#
def loginUser(mongoClient, user):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    print(user)
    userInsideCollection = mongoClient.user_collection.find_one({
        "username":
        user['username'],
        "password":
        user['password']
    })
    print(userInsideCollection)
    if userInsideCollection:
        print("Login Successful!")
        return True
    print("Login Fail")
    return False  #need to add something to show that user on client side that they cannot login (wrong username or password)


#
def mongoCreatePost(mongoClient, post):
    postID = mongoClient.post_collection.insert_one(post).inserted_id
    print("successful post", postID)
    return postID


#
def mongoGetPost(mongoClient, postID):
    return mongoClient.post_collection.find_one({"_id": ObjectId(postID)})


#
def mongoGetAllPosts(mongoClient):
    return list(mongoClient.post_collection.find())