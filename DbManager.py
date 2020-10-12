from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.db
collection = db['postings']

def insert(posting):
    return collection.insert_one(posting).acknowledged

def insert_all(postings):
    return collection.insert_many(postings)

def update(filter, update):
    return collection.update_one(filter, update).acknowledged

def delete(filter):
    return collection.delete_one(filter).acknowledged

def find(id):
    return collection.find_one(id)

def find_all():
    return collection.find()
