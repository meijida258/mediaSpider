import pandas as pd
from DB.Mongo import MongoSet
DataFilesPath = '../DataFiles/'

mon = MongoSet()

# artists = mon.artists_collection.find({}, {'_id':0, 'artist_id':1, 'artist_name':1, 'artist_from_country':1})

class myDict(dict):
    def __init__(self):
        super().__init__()

