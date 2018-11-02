import pandas as pd
from DB.Mongo import MongoSet
DataFilesPath = '../DataFiles/'
import itertools

mon = MongoSet()

def write_csv(data,data_count, write_step,csv_name):
    data_iter = (i for i in data) # 数据写入生成器
    for i in range(0, data_count, write_step):
        data_df = pd.DataFrame(list(itertools.islice(data_iter, 0, write_step)))
        if i == 0:
            data_df.to_csv(DataFilesPath + '{}.csv'.format(csv_name), index=False)
        else:
            data_df.to_csv(DataFilesPath + '{}.csv'.format(csv_name), mode='a', header=False, index=False)

def get_musics_data():
    musics = mon.musics_collection.find({}, {'_id': 0, 'music_album_id': 1, 'music_popularity': 1, 'music_title': 1,
                                             'artist_id': 1, 'music_duration': 1, 'music_id': 1})
    write_csv(musics, musics.count(), 10000, 'musics')

def get_artists_data():
    artists = mon.artists_collection.find({}, {'_id':0, 'artist_id':1, 'artist_name':1, 'artist_from_country':1})
    write_csv(artists, artists.count(), 5000, 'artists')

def get_albums_data():
    albums = mon.albums_collection.find({}, {'_id': 0, 'artist_id': 1, 'album_id': 1, 'album_title': 1, 'album_size':1})
    write_csv(albums, albums.count(), 5000, 'albums')

def get_comments_data():
    comments = mon.comments_collection.find({}, {'_id': 0, 'artist_id': 1, 'music_id': 1, 'total_comments': 1, 'music_comments':1})
    write_csv(comments, comments.count(), 10000, 'comments')

if __name__ == '__main__':
    # get_artists_data()
    get_albums_data()
    # get_comments_data()