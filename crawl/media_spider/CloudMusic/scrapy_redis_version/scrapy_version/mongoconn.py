from pymongo import MongoClient

# crwal_type  0--未开始 1--已开始 2--完成
class Mongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.CloudMusic
        self.artist_collection = self.db.Artist
        self.music_collection = self.db.Music

if __name__ == '__main__':
    mongo = Mongo()
else:
    mongo = Mongo()