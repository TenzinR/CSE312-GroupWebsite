from pymongo import MongoClient


class Client:
    def __init__(self):

        self.client = MongoClient("localhost", 27017)
        print("MONGO CONNECTION OPEN!")
        self.db = self.client.reddit_clone
        self.user_collection = self.db.user_collection
        self.chat_collection = self.db.chat_collection
        self.post_collection = self.db.post_collection


def registerUser(client, user):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    #TO-DO: check if username exists
    usernameTaken = client.user_collection.find_one(
        {"username": user['username']})
    if usernameTaken:
        print("Registration Failed")
        return False  #need to add something to show user on client side that username is taken
    client.user_collection.insert_one(user)
    print("Registration Successful!")
    return True


def loginUser(client, user):
    #user is a dictionary ex: {'username': Tenzin, 'password' : MyCoolPassword}
    print(user)
    userInsideCollection = client.user_collection.find_one({
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
