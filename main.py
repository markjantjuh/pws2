__author__ = 'MarkJan'

from Tkinter import *
from ttk import *
import tkSnack
import pickle
from track_pool import *
import tkFileDialog


class MusicApplication(Frame):
    def __init__(self, master):
        # standard variables
        self.count = 0
        self.locations = ['']

        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = True
        options['parent'] = root
        options['title'] = 'Select library location'

        #set up frame
        frame = Frame(master)
        Frame.__init__(frame)
        frame.pack()

        #set up music files and libraries
        self.track_pool = TrackPool()
        self.track_pool.clean_track_pool()
        self.track_pool.load_dir(self.locations[0])
        self.current_tracklist = CurrentTracklist()
        self.current_tracklist.reset()


        #listbox tracklist
        self.tracklistListBox = Treeview(master)
        self.tracklistListBox['columns'] = ('songtitle', 'artist', 'album', 'genre', 'length')
        self.tracklistListBox.heading("#0", text='', anchor='w')
        self.tracklistListBox.column("#0", anchor="w")
        self.tracklistListBox.heading("songtitle", text="Track")
        self.tracklistListBox.heading("artist", text="Artist")
        self.tracklistListBox.heading("album", text="Album")
        self.tracklistListBox.heading("genre", text="Genre")
        self.tracklistListBox.heading("length", text="Length")
        self.tracklistListBox.height = 3
        self.tracklistListBox.pack()
        self.update_tracklistbox()

        #edit track toolbar
        self.edit_tagsButton = Button(frame, text="Edit tags")
        self.edit_tagsButton.bind("<Button-1>", self.edit_tags_window)
        self.edit_tagsButton.pack()

        #initialize player
        tkSnack.initializeSnack(master)
        self.soundObject = tkSnack.Sound()
        self.queueBox = Treeview(master)
        self.queueBox['columns'] = ('songtitle', 'length')
        self.queueBox.heading('#0', text='', anchor='w')
        self.queueBox.column("#0", anchor="w")
        self.queueBox.heading("songtitle", text="Track")
        self.queueBox.heading("length", text="Length")
        self.queueBox.pack()

        #play button
        self.playButton = Button(frame, text="Play")
        self.playButton.bind("<Button-1>", self.playSound)
        self.playButton.pack(side=LEFT)

        #stop button
        self.stopButton = Button(frame, text="Stop")
        self.stopButton.bind("<Button-1>", self.stopSound)
        self.stopButton.pack(side=LEFT)

        self.add_to_queue_button = Button(frame, text="Add selected to queue")
        self.add_to_queue_button.bind("<Button-1>", self.add_to_queue)
        self.add_to_queue_button.pack(side=LEFT)

        self.add_to_playlist_button = Button(frame, text='add to playlist')
        self.add_to_playlist_button.bind("<Button-1>", self.add_to_playlist)
        self.add_to_playlist_button.pack()

        self.full_library_button = Button(frame, text='show full library')
        self.full_library_button.bind("<Button-1>", self.show_full_library)
        self.full_library_button.pack()

        self.remove_tracks_from_playlist_button = Button(frame, text="Remove selected tracks from playlist")
        self.remove_tracks_from_playlist_button.bind("<Button-1>", self.remove_from_playlist)
        self.remove_tracks_from_playlist_button.pack()

        #pause button
        self.pauseButton = Button(frame, text="Pause")
        self.pauseButton.bind("<Button-1>", self.pauseSound)
        self.pauseButton.pack(side=LEFT)

        #menu widget
        self.menu = Menu(master)
        root.config(menu=self.menu)

        #file submenu
        self.fileMenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="File locations", command=self.select_library_locations_window)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=None)

        #edit submenu
        self.editMenu = Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.editMenu)
        self.editMenu.add_command(label="Edit tags", command=self.edit_tags_window)

        #play submenu
        self.playMenu = Menu(self.menu)
        self.menu.add_cascade(label="Play", menu=self.playMenu)
        self.playMenu.add_command(label="Play", command=self.playSound)
        self.playMenu.add_command(label="Stop", command=self.stopSound)
        self.playMenu.add_command(label="Pause", command=self.pauseSound)

        #playlists submenu
        self.playlistsMenu = Menu(self.menu)
        self.menu.add_cascade(label="Playlists", menu=self.playlistsMenu)
        self.playlistsMenu.add_command(label="Add playlist", command=self.create_playlist_window)

        #songprogress bar
        self.songprogressBar = Scale(master, from_=0, to=128, command=None)
        self.songprogressBar.pack()

        #playlists listbox
        self.playlistsBox = Treeview(master)
        self.playlistsBox['columns'] = ('playlist', 'n_tracks')
        self.playlistsBox.heading('#0', text='', anchor='w')
        self.playlistsBox.column("#0", anchor="w")
        self.playlistsBox.heading("playlist", text="Playlist")
        self.playlistsBox.heading("n_tracks", text="Tracks")
        self.playlistsBox.pack()
        self.update_tracklistbox()
        self.update_playlistbox()

        self.playlistsBox.bind('<<TreeviewSelect>>', self.playlist_selection_change)

    def playlist_selection_change(self, event=None):
        selected_playlists = self.playlistsBox.selection()
        playlists = []
        for i in selected_playlists:
            playlists.append(self.track_pool.get_playlist_by_id(i))

        for i in playlists:
            self.playlist_to_current_tracklist(i)

        self.update_tracklistbox()

    def playlist_to_current_tracklist(self, playlist):
        self.current_tracklist.list = []
        for p in playlist.tracks:
            self.current_tracklist.list.append(p)


    def show_full_library(self, event=None):
        self.current_tracklist.reset()
        self.update_tracklistbox()

    def add_to_queue(self, event=None):
        selected_tracks = self.tracklistListBox.selection()
        for i in selected_tracks:
            print i
            t = self.track_pool.get_track_by_id(i)

            if t:
                self.queueBox.insert("", "end", t.id, values=(t.song_title, 0))  # t.length)
            else:
                print 'no track selected'

    def select_library_locations_window(self, event=None):
        self.count += 1
        id = "New window #%s" % self.count
        self.window = Toplevel(root)
        listbox = Listbox(self.window)
        for i in self.locations:
            listbox.insert(END, i)

        Button(self.window, text='askopenfile', command=self.askdirectory).pack(side=LEFT)
        listbox.pack(side=LEFT)

    def askdirectory(self):
        directory = tkFileDialog.askdirectory(**self.dir_opt)
        self.locations.append(directory)
        self.track_pool.load_dir(directory)
        self.track_pool.update_track_pool()
        self.current_tracklist.list = self.track_pool.track_pool_list
        self.update_tracklistbox()
        self.window.destroy()

    def playSound(self, event=None):
        p = self.queueBox.selection()
        t = self.track_pool.get_track_by_id(p[0])
        self.soundObject.load(t.path)
        self.soundObject.play()

    def stopSound(self, event=None):
        self.soundObject.stop()

    def pauseSound(self, event=None):
        self.soundObject.pause()

    def edit_tags_window(self, event=None):
        self.count += 1
        id = "New window #%s" % self.count
        self.tag_window = Toplevel(root)

        selected_tracks = self.tracklistListBox.selection()
        t = self.track_pool.get_track_by_id(selected_tracks[0])

        genre_label = Label(self.tag_window, text='Genre')
        genre_label.pack()
        genre_entry = Entry(self.tag_window)
        genre_entry.insert(0, self.track_pool.remove_pickle_crap(t.genre))
        genre_entry.pack()

        song_title_label = Label(self.tag_window, text='Song Title')
        song_title_label.pack()
        song_title_entry = Entry(self.tag_window)
        song_title_entry.insert(0,self.track_pool.remove_pickle_crap(t.song_title))
        song_title_entry.pack()

        artist_label = Label(self.tag_window, text='Song Title')
        artist_label.pack()
        artist_entry = Entry(self.tag_window)
        artist_entry.insert(0, self.track_pool.remove_pickle_crap(t.artist))
        artist_entry.pack()

        album_label = Label(self.tag_window, text='Song Title')
        album_label.pack()
        album_entry = Entry(self.tag_window)
        album_entry.insert(0, self.track_pool.remove_pickle_crap(t.album))
        album_entry.pack()

        Button(self.tag_window, text='save stuff',
               command=lambda: self.update_tags(t, genre_entry.get(), song_title_entry.get(), artist_entry.get(),
                                                album_entry.get())).pack()

    def update_tags(self, trackobj, genre, song_title, artist, album):
        trackobj.edit_tags(genre, song_title, artist, album)
        self.track_pool.update_track_pool()
        self.current_tracklist.update()
        self.update_tracklistbox()
        self.tag_window.destroy()

    def update_tracklistbox(self):
        for i in self.tracklistListBox.get_children():
            self.tracklistListBox.delete(i)

        for i in self.current_tracklist.list:
            self.tracklistListBox.insert("", "end", i.id,
                                         values=(self.track_pool.remove_pickle_crap(i.song_title),
                                                 self.track_pool.remove_pickle_crap(i.artist),
                                                 self.track_pool.remove_pickle_crap(i.album),
                                                 self.track_pool.remove_pickle_crap(i.genre),
                                                 self.track_pool.remove_pickle_crap(i.length_string)
                                                 ))

    def update_playlistbox(self):
        for i in self.playlistsBox.get_children():
            self.playlistsBox.delete(i)

        self.track_pool.update_track_pool()
        self.track_pool.update_playlists()

        for i in self.track_pool.playlists_list:
            self.playlistsBox.insert("", "end", i.id, values=(i.name, len(i.tracks)))

    def create_playlist_window(self):
        self.count += 1
        id = "New window #%s" % self.count
        self.playlist_window = Toplevel(root)

        playlist_name_label = Label(self.playlist_window, text='Name')
        playlist_name_label.pack()
        playlist_name_entry = Entry(self.playlist_window)
        playlist_name_entry.pack()

        Button(self.playlist_window, text='save stuff',
               command=lambda: self.create_playlist(playlist_name_entry.get())).pack()

    def create_playlist(self, name):
        self.track_pool.create_playlist(name)
        self.playlist_window.destroy()

        self.update_playlistbox()

    def add_to_playlist(self, event=None):
        track_selection = self.tracklistListBox.selection()

        self.count += 1
        id = "New window #%s" % self.count
        self.add_to_playlist_window = Toplevel(root)

        playlist_listbox = Treeview(self.add_to_playlist_window)

        playlist_listbox['columns'] = ('playlist', 'n_tracks')
        playlist_listbox.heading('#0', text='', anchor='w')
        playlist_listbox.column("#0", anchor="w")
        playlist_listbox.heading("playlist", text="Playlist")
        playlist_listbox.heading("n_tracks", text="Tracks")
        playlist_listbox.pack()

        for i in self.track_pool.playlists_list:
            playlist_listbox.insert("", "end", i.id, values=(i.name, len(i.tracks)))

        Button(self.add_to_playlist_window, text='save stuff',
               command=lambda: self.add_tracks_to_playlist(playlist_listbox.selection()[0], track_selection)).pack()

    def add_tracks_to_playlist(self, playlist, tracks):
        p = self.track_pool.get_playlist_by_id(playlist)
        y = []
        for i in tracks:
            y.append(self.track_pool.get_track_by_id(i))

        p.add_tracks(y)
        self.playlist_to_current_tracklist(p)
        self.track_pool.update_playlists()
        self.update_playlistbox()
        self.update_tracklistbox()

    def remove_from_playlist(self, event=None):
        playlist = self.playlistsBox.selection()[0]
        p = self.track_pool.get_playlist_by_id(playlist)

        tracks = self.tracklistListBox.selection()
        y = []

        for i in tracks:
            y.append(self.track_pool.get_track_by_id(i))

        p.remove_tracks(y)
        self.playlist_to_current_tracklist(p)
        self.track_pool.update_playlists()
        self.update_playlistbox()
        self.update_tracklistbox()

root = Tk()
app = MusicApplication(root)

root.mainloop()
