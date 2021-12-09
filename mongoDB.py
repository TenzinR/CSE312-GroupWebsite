from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt


class Client:
    def __init__(self):
        self.host = 'localhost'  #mongo for docker, localhost otherwise
        self.client = MongoClient(self.host, 27017)
        self.db = self.client.reddit_clone
        self.user_collection = self.db.user_collection
        self.chat_collection = self.db.chat_collection
        self.post_collection = self.db.post_collection
        self.online_users = self.db.online_users


def hashPassword(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def checkPassword(userObj, dbUser):
    return bcrypt.checkpw(userObj['password'].encode(),
                          dbUser['password'].encode())


def validateToken(mongoClient, token):
    userList = getAllUsers(mongoClient)
    for user in userList:
        if bcrypt.checkpw(str(user['_id']).encode(), token.encode()):
            return user
    return False


def toggleDarkmode(mongoClient, userID):
    user = mongoClient.user_collection.find_one({"_id": ObjectId(userID)})
    if "darkmode" in user:
        mongoClient.user_collection.find_one_and_update(
            {"_id": ObjectId(userID)},
            {'$set': {
                'darkmode': not user["darkmode"]
            }})
        return not user["darkmode"]
    mongoClient.user_collection.find_one_and_update(
        {"_id": ObjectId(userID)}, {'$set': {
            'darkmode': True
        }})
    return True


def getDarkmodeStatus(mongoClient, userID):
    user = mongoClient.user_collection.find_one({'_id': ObjectId(userID)})
    if 'darkmode' in user:
        return user['darkmode']
    return False


def getOnlineUsers(mongoClient):
    return mongoClient.online_users.find()


def addOnlineUser(mongoClient, userObj):
    try:
        return mongoClient.online_users.insert_one(userObj)
    except:
        return False


def removeOnlineUser(mongoClient, userObj):
    try:
        return mongoClient.online_users.delete_one(userObj)
    except:
        return False


#
def registerUser(mongoClient, userObj):
    userObj['password'] = hashPassword(userObj['password'])
    usernameTaken = mongoClient.user_collection.find_one(
        {"username": userObj['username']})
    if usernameTaken:
        return False  #need to add something to show user on client side that username is taken
    mongoClient.user_collection.insert_one(userObj)
    return True


#
def loginUser(mongoClient, userObj):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    #find user in the database with matching username
    dbUser = mongoClient.user_collection.find_one(
        {"username": userObj['username']})

    #if user with matching username exists, check if passwords match
    if dbUser:
        #userObj password unhashed, dbUser password is hashed
        if checkPassword(userObj, dbUser):
            return dbUser
    return False
    #need to add something to show that user on client side that they cannot login (wrong username or password)


def getAllUsers(mongoClient):
    return list(mongoClient.user_collection.find())


#
def mongoCreatePost(mongoClient, post):
    postID = mongoClient.post_collection.insert_one(post).inserted_id
    return postID


#
def mongoGetPost(mongoClient, postID):
    return mongoClient.post_collection.find_one({"_id": ObjectId(postID)})


def mongoAddPostToUser(mongoClient, postID, authorID):
    author = mongoClient.user_collection.find_one_and_update(
        {"_id": ObjectId(authorID)}, {'$push': {
            'postList': postID
        }})
    return


def mongoGetUserPosts(mongoClient, userID):
    try:
        postIDs = mongoClient.user_collection.find_one(
            {"_id": ObjectId(userID)})['postList']
    except:
        postIDs = []
    postInfoList = []
    for id in postIDs:
        post = mongoGetPost(mongoClient, id)
        post['_id'] = str(post['_id'])
        postInfoList.append(post)
    return postInfoList


#
def mongoGetAllPosts(mongoClient):
    return list(mongoClient.post_collection.find())
