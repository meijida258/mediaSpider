
from pymongo import MongoClient


class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.CloudMusic

        self.albums_collection = self.db.Albums
        self.artists_collection = self.db.Artists
        self.comments_collection = self.db.MusicComments
        self.musics_collection = self.db.Musics

if __name__ == '__main__':
    mongo = MongoSet()
