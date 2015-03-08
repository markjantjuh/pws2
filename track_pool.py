__author__ = 'MarkJan'
import cPickle as pickle
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import os.path
import uuid
import random
import re

#class that defines a trackpool object linked to the musicapplication, contains list of loaded tracks, playlists and options for handling the current session
class TrackPool:
    def __init__(self):
        self.track_list_location = 'Output/init_files/tracklist.pkl' #set location for file where all track objects are saved
        self.playlists_location = 'Output/init_files/playlists.pkl' #set location for file where all playlist objects are saved
        self.locations_loaction = 'Output/init_files/locations.pkl' #set location for file where all locations are saved

        self.load_track_pool_list() #load trackpool
        self.load_playlists_list() #load playlists
        self.load_locations_list() #load locations

    #gets all existing trackpool objects
    def load_track_pool_list(self):
        try:
            with open(self.track_list_location, 'rb') as input:
                self.track_pool_list = pickle.load(input)
                print 'ok', self.track_pool_list
        except EOFError:
            print 'empty tracklist'
            self.track_pool_list = []

        return self.track_pool_list

    #gets all existing playlists
    def load_playlists_list(self):
        try:
            with open(self.playlists_location, 'rb') as input:
                self.playlists_list = pickle.load(input)
                print 'ok', self.playlists_list
        except EOFError:
            print 'empty tracklist'
            self.playlists_list = []

        return self.playlists_list

    #gets all existing locations
    def load_locations_list(self):
        try:
            with open(self.locations_loaction, 'rb') as input:
                x = pickle.load(input)
                self.locations_list = []
                for i in x:
                    self.locations_list.append(self.remove_pickle_crap(i))

        except EOFError:
            self.locations_list = []

        return self.locations_list

    #function that saves the locationlist to file
    def save_locations_list(self):
        if self.locations_list:
            with open(self.locations_loaction, 'wb') as output:
                pickle.dump(self.locations_list, output, -1)

    #function that creates a playlistobject and appends it to the playlistslist
    def create_playlist(self, name):
        self.playlists_list.append(Playlist(name))
        self.update_playlists()

    #function that writes playlistslist to file
    def update_playlists(self):
        if self.playlists_list:
            with open(self.playlists_location, 'wb') as output:
                pickle.dump(self.playlists_list, output, -1)

    def get_track_by_id(self, id):
        print 'trackid', id
        for i in self.track_pool_list:
            if int(i.id) == int(id):
                return i

        return None

    def get_playlist_by_id(self, id):
        print 'playlistid', id

        for i in self.playlists_list:
            if int(i.id) == int(id):
                return i

        return None

    def update_track_pool(self):
        if self.track_pool_list:
            with open(self.track_list_location, 'wb') as output:
                pickle.dump(self.track_pool_list, output, -1)

    def clean_track_pool(self):
        for track in self.track_pool_list:
            if not os.path.isfile(track.path):
                print 'Removed ' + track.path + ' from library'
                self.track_pool_list.remove(track)

        self.update_track_pool()

    def refresh_trackpool(self):
        try:
            with open(self.track_list_location, 'rb') as input:
                self.track_pool_list = pickle.load(input)
                print 'ok', self.track_pool_list
        except EOFError:
            print 'empty tracklist'
            self.track_pool_list = []

    def refresh_playlists(self):
        try:
            with open(self.playlists_location, 'rb') as input:
                self.playlists_list = pickle.load(input)
                print 'ok', self.playlists_list
        except EOFError:
            print 'no playlists'
            self.playlists_list = []

    def load_dir(self):
        self.load_locations_list()
        for i in self.locations_list:
            for subdir, dirs, files in os.walk(i):
                print 'okaas2'
                for file in files:
                    if file.endswith('.mp3') or file.endswith('.wav'):
                        with Closer(TrackPool()) as x:
                            p = os.path.realpath(os.path.join(subdir,file))
                            if not x.track_in_pool(p):
                                x.track_pool_list.append(Track(p))
                                print 'added:', p
                                x.update_track_pool()

    def track_in_pool(self, path):
        for track in self.track_pool_list:
            if track.path == path:
                return True

        return False

    def remove_pickle_crap(self, text):
        s1 = "\[u'"
        s2 = "'\]"

        print str(text)

        try:
            found = re.search('%s(.*?)%s' % (s1, s2), str(text)).group(1)
            return found
        except AttributeError:
            return text

class Track:
    def __init__(self, path, genre=None, song_title=None, artist=None, album=None, year=None, bpm=None, key=None):
        self.path = path
        p = uuid.uuid4()
        self.id = int(p)

        self.hidden = False

        print self.path
        if self.path.endswith('.mp3'): self.setup_mp3(self.path, genre, song_title, artist, album, year, bpm, key)
        if self.path.endswith('.wav'): self.setup_wav(self.path, genre, song_title, artist, album, year, bpm, key)

        print 'pls'

    def setup_mp3(self, path, genre, song_title, artist, album, year, bpm, key):
        audio = MP3(path, ID3=EasyID3)

        self.length = audio.info.length

        self.length_h = int(self.length / 3600)
        self.length_m = int(self.length / 60) % 60
        self.length_s = int(self.length) % 60

        self.length_string = str(self.length_h).zfill(2) + ':' + str(self.length_m).zfill(2) + ':' + str(self.length_s).zfill(2)

        self.genre      = (audio['genre']  if genre==None       else genre)
        self.song_title = (audio['title']  if song_title==None  else song_title)
        self.artist     = (audio['artist'] if artist==None      else artist)
        self.album      = (audio['album']  if album==None       else album)

    def setup_wav(self, path,genre, song_title, artist, album, year, bpm, key):
        pass

    def edit_tags(self, genre, song_title, artist, album):
        self.genre = genre
        self.song_title = song_title
        self.artist = artist
        self.album = album

    def edit_mp3_tags(self):
        audio = MP3(self.path, ID3=EasyID3)

        audio['genre'] = self.genre
        audio['title'] = self.song_title
        audio['artist'] = self.artist
        audio['album'] = self.album
        audio.save()

class CurrentTracklist:
    def __init__(self):
        self.reset()
        self.list = []

    def shuffle(self):
        random.shuffle(self.list)

    def reset(self):
        with Closer(TrackPool()) as x:
            print x, 'kurwa'
            self.list = x.track_pool_list

    def add_tracks(self, list):
        for i in list:
            self.list.append(i)

    def remove_tracks(self, list):
        for i in list:
            self.list.remove(i)

    def clear(self):
        self.list = []

    def remove_duplicates(self):
        pass

    def update(self):
        x = []
        for i in self.list:
            x.append(i.id)

        self.reset()
        self.list = []

        for i in x:
            with Closer(TrackPool()) as t:
                m = t.get_track_by_id(i)
                self.list.append(m)

class Closer:
    '''A context manager to automatically close an object with a close method
    in a with statement.'''

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        try:
           self.obj.close()
        except AttributeError: # obj isn't closable
           print 'Not closable.'
           return True # exception handled successfully

class Playlist:
    def __init__(self, name, tracks=None):
        self.name = name
        self.tracks = ([]  if tracks==None else tracks)

        p = uuid.uuid4()
        self.id = int(p)

    def add_tracks(self, track_ids):
        for i in track_ids:
            self.tracks.append(i)

    def remove_tracks(self, tracks):
        for i in tracks:
            x = self.get_track_by_id(i)
            self.tracks.remove(x)


    def get_track_by_id(self, trackid):
        for i in self.tracks:
            print i.id, 'trackid asked'

            print trackid.id
            if int(i.id) == int(trackid.id):
                return i

        return None


