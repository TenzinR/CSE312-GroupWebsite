from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt


class Client:
    def __init__(self):

        self.client = MongoClient("localhost", 27017)
        print("MONGO CONNECTION OPEN!")
        self.db = self.client.reddit_clone
        self.user_collection = self.db.user_collection
        self.chat_collection = self.db.chat_collection
        self.post_collection = self.db.post_collection


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
            return True
    return False


#
def registerUser(mongoClient, userObj):
    userObj['password'] = hashPassword(userObj['password'])
    usernameTaken = mongoClient.user_collection.find_one(
        {"username": userObj['username']})
    if usernameTaken:
        print("Registration Failed")
        return False  #need to add something to show user on client side that username is taken
    mongoClient.user_collection.insert_one(userObj)
    print("Registration Successful!")
    return True


#
def loginUser(mongoClient, userObj):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    print(userObj)

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
    print("successful post", postID)
    return postID


#
def mongoGetPost(mongoClient, postID):
    return mongoClient.post_collection.find_one({"_id": ObjectId(postID)})


#
def mongoGetAllPosts(mongoClient):
    return list(mongoClient.post_collection.find())
