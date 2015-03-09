__author__ = 'MarkJan'

from Tkinter import *       #tkinter import
from ttk import *           #ttk import
import tkSnack              #sound module import
from track_pool import *    #connection with trackpool
import tkFileDialog         #file dialog import

class MusicApplication(Frame):
    #app written as class
    '''init function'''
    def __init__(self, master):
        self.count = 0 #windowcount

         #set up frame
        frame = Frame(root)
        Frame.__init__(frame)
        frame.pack()

        #making reference to window dedicated to player
        self.player_window = None

        #set up trackpool
        self.track_pool = TrackPool() #make object
        self.track_pool.load_dir()
        self.track_pool.clean_track_pool() #check whether all tracks still exist, updates track pool

        #defines the tracks that are currently in use, these tracks will be displayed in the TrackListBox
        self.current_tracklist = CurrentTracklist()
        self.current_tracklist.reset() #write full library to current tracklist

        #initializing variables
        self.queue = []
        self.queueBox_count = IntVar() #amount of tracks in the queueBox
        self.current_tracklist_count = IntVar() #amount of tracks in the current tracklist

        #execute UI functions
        self.main_window()
        self.main_menu()

        #initialize player object
        self.initialize_player()

        #fill all listboxes with info
        self.update_tracklistbox()
        self.update_playlistbox()

    '''UI FUNCTIONS'''
    def main_window(self):
        #set up frames
        self.main_window_topframe = Frame(root)
        self.main_window_bottomframe = Frame(root)

        # * * * * * * * * * * * * * TOP FRAME * * * * * * * * * * *
        self.main_window_topframe.rowconfigure(0, weight=1)
        self.main_window_topframe.columnconfigure(0, weight=1)

        #listbox current tracklist
        self.tracklistListBox = Treeview(self.main_window_topframe) #ttk Treeview
        self.tracklistListBox['columns'] = ('songtitle', 'artist', 'album', 'genre', 'length') #define Treeview columns
        self.tracklistListBox.heading("#0", text='', anchor='w')
        self.tracklistListBox.column("#0", anchor="w")

        #add headings to Treeview columns
        for col in self.tracklistListBox['columns']:
            self.tracklistListBox.heading(col, text=col, command=lambda col_=col: self.treeview_sort(self.tracklistListBox, col_, False))
        #placing tracklistBox UI-elements on the UI

        self.tracklistListBox.grid(row=0, column=0, sticky=N+S+E+W) #placing traclistBox

        #adding a scrollbar to current_tracklist Listbox
        self.tracklistListBox_scrollbar = Scrollbar(root, orient='vertical', command=self.tracklistListBox.yview) #tkinter Scrollbar
        self.tracklistListBox_scrollbar.pack()

        #placing label connected to current_tracklist_count
        Label(self.main_window_topframe, textvariable=self.current_tracklist_count).grid(row=0, column=2)

        #edit tags_button
        self.edit_tagsButton = Button(root, text="Edit tags") #tkinter Button
        self.edit_tagsButton.bind("<Button-1>", self.edit_tags_window) #bind button to function edit_tags_window()
        self.edit_tagsButton.pack()

        self.hide_tracks_from_pool = Button(root, text="hide selection")
        self.hide_tracks_from_pool.bind("<Button-1>", self.hide_selected_tracks)
        self.hide_tracks_from_pool.pack()

        self.reset_hidden = Button(root, text="reset hidden")
        self.reset_hidden.bind("<Button-1>", self.reset_hidden_tracks)
        self.reset_hidden.pack()

        #create button to open player window
        Button(root, text='open player', command=self.player_window_go).pack()

        #button to add selected tracks to queue
        self.add_to_queue_button = Button(root, text="Add selected to queue") #create Tkinter Button
        self.add_to_queue_button.bind("<Button-1>", self.add_to_queue) #bind button to add_to_queue function
        self.add_to_queue_button.pack(side=LEFT)

        #button to add every track in current_tracklist to queue
        self.add_everything_to_queue = Button(root, text="Add everything to queue") #create Tkinter Button
        self.add_everything_to_queue.bind("<Button-1>", self.add_to_queue) #bind button to add_to_queue function
        self.add_everything_to_queue.pack()

        #button to add selected tracks to playlist
        self.add_to_playlist_button = Button(root, text='add to playlist') #create Tkinter Button
        self.add_to_playlist_button.bind("<Button-1>", self.add_to_playlist) #bind button to add_to_playlist function
        self.add_to_playlist_button.pack()

        #button to 'reset' the current_tracklist_and listbox
        self.full_library_button = Button(root, text='show full library') #create Tkinter Button
        self.full_library_button.bind("<Button-1>", self.show_full_library) #bind button to show_full_library function
        self.full_library_button.pack()

        #button to remove selected tracks from selected playlist
        self.remove_tracks_from_playlist_button = Button(root, text="Remove selected tracks from playlist") #create Tkinter Button
        self.remove_tracks_from_playlist_button.bind("<Button-1>", self.remove_from_playlist) #bind button to remove_from_playlist function
        self.remove_tracks_from_playlist_button.pack()

        self.remove_playlist_button = Button(root, text="Remove selected playlist") #create Tkinter Button
        self.remove_playlist_button.bind("<Button-1>", self.remove_playlist)
        self.remove_playlist_button.pack()

        #options for the tkFileDialog
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = True
        options['parent'] = root
        options['title'] = 'Select library location'

    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort(tv, col, not reverse))

    def main_menu(self):
        #creating menu widget
        self.menu = Menu(root)
        root.config(menu=self.menu)

        #file submenu
        self.fileMenu = Menu(self.menu) #create Tkinter Menu
        self.menu.add_cascade(label="File", menu=self.fileMenu) #add cascade File
        self.fileMenu.add_command(label="File locations", command=self.select_library_locations_window) #command to select library locations
        self.fileMenu.add_separator() #seperator
        self.fileMenu.add_command(label="Exit", command=root.quit) #command to quit the application

        #edit submenu
        self.editMenu = Menu(self.menu) #create Tkinter menu
        self.menu.add_cascade(label="Edit", menu=self.editMenu) #add cascade Edit
        self.editMenu.add_command(label="Edit tags", command=self.edit_tags_window) #command to edit tags

        #play submenu
        self.playMenu = Menu(self.menu) #create Tkinter menu
        self.menu.add_cascade(label="Play", menu=self.playMenu) #add cascade Play
        self.playMenu.add_command(label="Play", command=self.playSound) #command to start playing sound
        self.playMenu.add_command(label="Stop", command=self.stopSound) #command to stop playing sound
        self.playMenu.add_command(label="Pause", command=self.pauseSound) #command to pause the sound

        #playlists submenu
        self.playlistsMenu = Menu(self.menu) #create Tkinter menu
        self.menu.add_cascade(label="Playlists", menu=self.playlistsMenu) #add cascade Playlists
        self.playlistsMenu.add_command(label="Add playlist", command=self.create_playlist_window) #command to create new playlist

        #listbox with playlists
        self.playlistsBox = Treeview(root) #ttk TreeView
        self.playlistsBox['columns'] = ('playlist', 'n_tracks')
        self.playlistsBox.heading('#0', text='', anchor='w')
        self.playlistsBox.column("#0", anchor="w")
        self.playlistsBox.heading("playlist", text="Playlist")
        self.playlistsBox.heading("n_tracks", text="Tracks")
        self.playlistsBox.pack()

        #add scrollbar to playlistbox
        self.playlistsBox_scrollbar = Scrollbar(root, orient='vertical', command=self.playlistsBox.yview)
        self.playlistsBox_scrollbar.pack()

        #bind selection change to function
        self.playlistsBox.bind('<<TreeviewSelect>>', self.playlist_selection_change)

    def playlist_selection_change(self, event=None):
        selected_playlists = self.playlistsBox.selection() #get selected playlists (ids)
        playlists = [] #empty list for playlists (objects)
        for i in selected_playlists:
            playlists.append(self.track_pool.get_playlist_by_id(i)) #get all playlist objects in the playlists list

        for i in playlists:
            self.playlist_to_current_tracklist(i) #write selected playlists to current tracklist

        self.update_tracklistbox() #update the tracklistbox with the newly formed current_tracklist

        #create a window to edit tags belonging to a track

    def edit_tags_window(self, event=None):
        self.count += 1
        id = "New window #%s" % self.count
        self.tag_window = Toplevel(root)
        self.tag_window.minsize(width=640, height=150)

        for i in range(5):
            self.tag_window.rowconfigure(i, weight=1)

        self.tag_window.columnconfigure(1, weight=1)

        #get first track from the selected tracks to edit
        selected_tracks = self.tracklistListBox.selection()
        t = self.track_pool.get_track_by_id(selected_tracks[0])

        self.tag_window.title('editing: ' + self.track_pool.remove_pickle_crap(str(t.song_title)))

        #create input information for genre
        #genre label
        genre_label = Label(self.tag_window, text='Genre')
        genre_label.grid(row=0, column=0, sticky=N+S)

        #genre entry
        genre_entry = Entry(self.tag_window)
        genre_entry.insert(0, self.track_pool.remove_pickle_crap(t.genre))
        genre_entry.grid(row=0, column=1, sticky=N+S+E+W)

        #create input information for song_title
        #song_title label
        song_title_label = Label(self.tag_window, text='Song Title')
        song_title_label.grid(row=1, column=0, sticky=N+S)

        #song_title entry
        song_title_entry = Entry(self.tag_window)
        song_title_entry.insert(0,self.track_pool.remove_pickle_crap(t.song_title))
        song_title_entry.grid(row=1, column=1, sticky=N+S+E+W)

        #create input information for artist
        #artist_label
        artist_label = Label(self.tag_window, text='Artist')
        artist_label.grid(row=2, column=0, sticky=N+S)

        #artist entry
        artist_entry = Entry(self.tag_window)
        artist_entry.insert(0, self.track_pool.remove_pickle_crap(t.artist))
        artist_entry.grid(row=2, column=1, sticky=N+S+E+W)

        #create input information for album
        #album label
        album_label = Label(self.tag_window, text='Album')
        album_label.grid(row=3, column=0, sticky=N+S)

        #album entry
        album_entry = Entry(self.tag_window)
        album_entry.insert(0, self.track_pool.remove_pickle_crap(t.album))
        album_entry.grid(row=3, column=1, sticky=N+S+E+W)

        edit_mp3_tags = IntVar()
        edit_mp3_tags_checkbox = Checkbutton(self.tag_window, variable=edit_mp3_tags, text='Edit tags of file (MP3 Only)')
        edit_mp3_tags_checkbox.grid(row=4, column=0, columnspan=2, sticky=N+S+E+W)

        #create button that sends all the user submitted information to update_tags function
        Button(self.tag_window, text='Save tags',
               command=lambda: self.update_tags(t, genre_entry.get(), song_title_entry.get(), artist_entry.get(),
                                                album_entry.get(), edit_mp3_tags.get())).grid(row=5, column=0, columnspan=2, sticky=N+S)

    def select_library_locations_window(self, event=None):
        self.count += 1
        id = "New window #%s" % self.count
        self.window = Toplevel(root) #create new window
        self.listbox = Listbox(self.window) #create new listbox

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.minsize(width=500, height=50)

        #insert all existing locations in listbox
        for i in self.track_pool.locations_list:
            self.listbox.insert(END, i)

        self.listbox.grid(row=0, column=0, rowspan=2, sticky=N+S+E+W)

        #create button to start searching
        Button(self.window, text='Add Directory', command=self.askdirectory).grid(row=0, column=1, sticky=E+W) #binded to askdir function
        Button(self.window, text='Remove Selected Directory', command=self.removedirectory).grid(row=1, column=1, sticky=E+W)

        #function to get a window that lets the user create a new playlist

    def create_playlist_window(self):
        self.count += 1
        id = "New window #%s" % self.count
        self.playlist_window = Toplevel(root)
        self.playlist_window.title('Create new playlist')
        self.playlist_window.minsize(width=300, height=100)

        self.playlist_window.rowconfigure(0, weight=1)
        self.playlist_window.columnconfigure(1, weight=1)

        #input for name of the new playlist
        #playlist_name label
        playlist_name_label = Label(self.playlist_window, text='Name')
        playlist_name_label.grid(row=0, column=0, sticky=N+S)

        #playlist_name entry
        playlist_name_entry = Entry(self.playlist_window)
        playlist_name_entry.grid(row=0, column=1, sticky=E+W)

        #button that sends user submitted information to create_playlist function
        Button(self.playlist_window, text='save stuff',
               command=lambda: self.create_playlist(playlist_name_entry.get())).grid(row=1, column=0, columnspan=2, sticky=E+W)

    #function that updates the contents of the tracklistbox
    def update_tracklistbox(self):
        #delete all items currently in the tracklistbox
        for i in self.tracklistListBox.get_children():
            self.tracklistListBox.delete(i)

        #insert all tracks from the current_tracklist into the trackpool
        self.track_pool.refresh_trackpool()
        for i in self.current_tracklist.list:
            q = self.track_pool.get_track_by_id(i.id)
            if q.hidden == False:
                self.tracklistListBox.insert("", "end", q.id,
                                         values=(self.track_pool.remove_pickle_crap(q.song_title),
                                                 self.track_pool.remove_pickle_crap(q.artist),
                                                 self.track_pool.remove_pickle_crap(q.album),
                                                 self.track_pool.remove_pickle_crap(q.genre),
                                                 self.track_pool.remove_pickle_crap(q.length_string)
                                                 ))


        #update the counter
        self.current_tracklist_count.set(len(self.tracklistListBox.get_children()))

    #update the playlistbox
    def update_playlistbox(self):
        #delete all items currently in the playlistbox
        for i in self.playlistsBox.get_children():
            self.playlistsBox.delete(i)

        #update everything
        self.track_pool.update_track_pool()
        self.track_pool.update_playlists()

        #insert all playlists into the playlist_box
        for i in self.track_pool.playlists_list:
            self.playlistsBox.insert("", "end", i.id, values=(i.name, len(i.tracks)))

        #function that resets the current tracklist and updates the tracklistbox

    def show_full_library(self, event=None):
        self.current_tracklist.reset()
        self.update_tracklistbox()

        #add tracks to playlist

    def add_to_playlist(self, event=None):
        #get selected tracks
        track_selection = self.tracklistListBox.selection()

        #create add_to_playlist window
        self.count += 1
        id = "New window #%s" % self.count
        self.add_to_playlist_window = Toplevel(root)
        self.add_to_playlist_window.minsize(width=300, height=100)
        self.add_to_playlist_window.title('Add selected tracks to playlist')

        self.add_to_playlist_window.rowconfigure(0, weight=1)
        self.add_to_playlist_window.columnconfigure(0, weight=1)

        #create listbox consisting of playlists that currently exist with the amount of items in it
        playlist_listbox = Treeview(self.add_to_playlist_window)
        playlist_listbox['columns'] = ('playlist', 'n_tracks')
        playlist_listbox.heading('#0', text='', anchor='w')
        playlist_listbox.column("#0", anchor="w")
        playlist_listbox.heading("playlist", text="Playlist")
        playlist_listbox.heading("n_tracks", text="Tracks")
        playlist_listbox.grid(row=0, column=0, sticky=N+S+E+W)

        #insert items into the newly created listbox
        for i in self.track_pool.playlists_list:
            playlist_listbox.insert("", "end", i.id, values=(i.name, len(i.tracks)))

        #create button that send the info to add_tracks_to_playlist
        Button(self.add_to_playlist_window, text='Add to playlist',
               command=lambda: self.add_tracks_to_playlist(playlist_listbox.selection()[0], track_selection)).grid(row=1, column=0)

    '''PLAYER WINDOW UI FUNCTIONS'''
    #creation of the player window
    def player_window_go(self):
        if self.player_window is None: #check if there is no player window already
            self.count += 1
            id = "New window #%s" % self.count

            #create new window
            self.player_window = Toplevel(root)
            self.player_window.protocol("WM_DELETE_WINDOW", self.player_window_onclose)
            self.player_window.columnconfigure(0, weight=1)
            self.player_window.rowconfigure(0, weight=1)

            self.player_window.title('Player')

            #create frames
            self.player_window_topframe = Frame(self.player_window)
            self.player_window_bottomframe = Frame(self.player_window)

            self.player_window_topframe.grid(row=0, sticky=N+S+E+W)
            self.player_window_bottomframe.grid(row=1, sticky=E+W)

            # * * * * * * * TOPFRAME * * * * * * *
            self.player_window_topframe.grid_rowconfigure(0, weight=1)
            self.player_window_topframe.grid_columnconfigure(0, weight=1)

            self.queueBox_scrollbar = Scrollbar(self.player_window_topframe)
            self.queueBox_scrollbar.grid(row=0, column=1, sticky=N+S)

            #create queueBox
            #queueBox contains tracks currently ready to play
            self.queueBox = Treeview(self.player_window_topframe, yscrollcommand=self.queueBox_scrollbar.set)
            self.queueBox_scrollbar.config(command=self.queueBox.yview)
            self.queueBox['columns'] = ('songtitle', 'length')
            self.queueBox.heading('#0', text='', anchor='w')
            self.queueBox.column("#0", anchor="w")
            self.queueBox.heading("songtitle", text="Track")
            self.queueBox.heading("length", text="Length")
            self.queueBox.grid(row=0, column=0, sticky=N+S+E+W)

            # * * * * * * * * * BOTTOM FRAME * * * * * * * * * *
            #add a bar to be able to set the volume
            for x in range(2):
                self.player_window_bottomframe.grid_rowconfigure(x, weight=1)
            for y in range(5):
                self.player_window_bottomframe.grid_columnconfigure(y, weight=1)

            self.volumeBar = Scale(self.player_window_bottomframe, from_=0, to=100, orient=VERTICAL, command=self.update_volume) #tkinter Scale
            self.volumeBar.set(50) #set init value
            self.volumeBar.grid(row=0, column=0, sticky=N+S+E+W)

            #volume text variable
            self.volume = StringVar()
            Label(self.player_window_bottomframe, textvariable=self.volume).grid(row=1, column=0, sticky=N+S+E+W) #label binded to self.volume
            self.volume.set(str(int(tkSnack.audio.play_gain())) + "%") #set volumetext

            #play button on player_window
            self.playButton = Button(self.player_window_bottomframe, text="Play") #create button on player_window
            self.playButton.bind("<Button-1>", self.playSound) #bind button to playSound function
            self.playButton.grid(row=0, column=1, sticky=N+E)

            #stop button on player_window
            self.stopButton = Button(self.player_window_bottomframe, text="Stop") #create button on player_window
            self.stopButton.bind("<Button-1>", self.stopSound) #bind button to stopSound function
            self.stopButton.grid(row=0, column=2, sticky=N+E)

            #pause button on player_window
            self.pauseButton = Button(self.player_window_bottomframe, text="Pause") #create button on player_Window
            self.pauseButton.bind("<Button-1>", self.pauseSound) #bind button to pauseSound function
            self.pauseButton.grid(row=1, column=1, sticky=N+E)

            #create button to go to next song from queue
            self.nextButton = Button(self.player_window_bottomframe, text="Next") #tkinter Button
            self.nextButton.bind("<Button-1>", self.play_next_from_queue) #button binded to play_next_from_queue function
            self.nextButton.grid(row=1, column=2, sticky=N+E)

            #update counter, amount of tracks in queue
            self.queuebox_update_count()
            Label(self.player_window_bottomframe, textvariable=self.queueBox_count).grid(row=0, column=3, sticky=N+S) #link counter to label (self-updating)

            #create button to remove selection from queue
            self.remove_from_queue_button = Button(self.player_window_bottomframe, text="Remove selected from queue")
            self.remove_from_queue_button.bind("<Button-1>", self.remove_selection_from_queue)
            self.remove_from_queue_button.grid(row=1, column=3, sticky=N+S+E+W)

            #add a bar to track the progress of the song
            self.songprogressBar = Scale(self.player_window_bottomframe, from_=0, to=128, command=None) #tkinter Scale
            self.songprogressBar.grid(row=0, column=4, sticky=N+S+E+W)

            #create time_elapsed string variable
            self.time_elapsed = StringVar()
            Label(self.player_window_bottomframe, textvariable=self.time_elapsed).grid(row=1, column=4, sticky=E+W) #bind timeelapsed to label

            #start loop of updating the time that elapsed after first song
            self.update_time_elapsed()

        #function that is executed when the player_window gets closed

    def player_window_onclose(self):
        self.player_window.destroy() #close window
        self.player_window = None #set player_window variable to None

        #function that updates the time that has elapsed

    def update_time_elapsed(self):
        q = int(tkSnack.audio.elapsedTime()) #get the elapsedTime since the last play() call from the soundObject

        p = self.soundObject.length(unit="SECONDS") #get length of the track currently playing

        #length_songstring calculations
        length_song_h = int(p / 3600) #get amount of hours for song
        length_song_m = int(p / 60) % 60 #get amount of minutes for song
        length_song_s = int(p) % 60 #get amount of seconds for song
        length_song_string = str(length_song_h).zfill(2) + ':' + str(length_song_m).zfill(2) + ':' + str(length_song_s).zfill(2) #create string out of everything for the song

        #length elapsed time calculations
        length_elapsed_h = int(q / 3600) #get amount of hours for time elapsed
        length_elapsed_m = int(q / 60) % 60 #get amount of minutes for time elapsed
        length_elapsed_s = int(q) % 60 #get amount of seconds for time elapsed
        length_elapsed_string = str(length_elapsed_h).zfill(2) + ':' + str(length_elapsed_m).zfill(2) + ':' + str(length_elapsed_s).zfill(2) #create string out of everything for the time elapsed

        total_string = length_elapsed_string + "/" + length_song_string #create string to be displayed with format time elapsed/length song

        self.time_elapsed.set(total_string) #set time elapsed string label to total_string

        #condition to prevent divide by zero error
        if self.soundObject.length() != 0:
            #calculate and set percentage song/length to set songprogressBar value
            self.time_elapsed_percentage = (tkSnack.audio.elapsedTime() / self.soundObject.length(unit="SECONDS"))* 100
            self.songprogressBar.set(self.time_elapsed_percentage)

        #make sure function gets executed every 100ms to keep the elapsed time updated
        root.after(100, self.update_time_elapsed)

    '''TRACKPOOL FUNCTIONS'''
    #function that asks for a directory to be selected
    def askdirectory(self):
        directory = tkFileDialog.askdirectory(**self.dir_opt) #create filedialog which returns a selected directory

        if directory not in self.track_pool.locations_list:
            self.track_pool.locations_list.append(directory)
            self.track_pool.save_locations_list()
            self.track_pool.load_dir()

            self.current_tracklist.reset()

        self.update_tracklistbox()

    def removedirectory(self):
        p = self.listbox.curselection()
        for i in p:
            del self.track_pool.locations_list[i]

        self.track_pool.save_locations_list()
        self.track_pool.load_dir()
        self.update_tracklistbox()

    #function that updates the tags from a specified track
    def update_tags(self, trackobj, genre, song_title, artist, album, edit_mp3):
        trackobj.edit_tags(genre, song_title, artist, album) #edit the tags on the trackobject

        if edit_mp3 == 1 and trackobj.path.endswith('.mp3'):
            trackobj.edit_mp3_tags()

        self.track_pool.update_track_pool() #update the trackpool
        self.current_tracklist.update() #update the current tracklist
        self.update_tracklistbox() #update the track_listbox with the updated current_tracklist
        self.tag_window.destroy() #destroy the update_tags window

    def hide_selected_tracks(self, event=None):
        selection = self.tracklistListBox.selection()
        for i in selection:
            p = self.track_pool.get_track_by_id(i)
            p.hidden = True

        self.track_pool.update_track_pool()
        self.update_tracklistbox()

    def reset_hidden_tracks(self, event=None):
        for i in self.track_pool.track_pool_list:
            i.hidden = False

        self.track_pool.update_track_pool()
        self.current_tracklist.reset()
        self.update_tracklistbox()

    '''QUEUE FUNCTIONS'''
    #function that adds selected tracks to the queueBox
    def add_to_queue(self, event=None):
        self.player_window_go() #open playerwindow

        #check whether it needs to add everything or add a selection
        if event.widget == self.add_everything_to_queue:
            selected_tracks = self.tracklistListBox.get_children()
        else:
            selected_tracks = self.tracklistListBox.selection()

        #for every track in selected_tracks, get the track object and append that to the queue
        for i in selected_tracks:
            print i
            t = self.track_pool.get_track_by_id(i)

            if t:
                self.queue.append(t)
            else:
                print 'no track selected'

        #insert all queue items into the queuebox
        self.update_queuebox()

        #update queuebox counter
        self.queuebox_update_count()

        #remove selected items from queue

    def update_queuebox(self, event=None):
        #remove all items in the queueBox
        for i in self.queueBox.get_children():
            self.queueBox.delete(i)

        #insert all queue items into queueBox
        for q in self.queue:
            self.queueBox.insert("", "end", q.id, values=(self.track_pool.remove_pickle_crap(q.song_title), q.length_string))  # t.length)

    def remove_from_queue(self, event=None):
        #remove first item in the queue
        del self.queue[0]
        self.update_queuebox()

    def remove_selection_from_queue(self, event=None):
        selection = self.queueBox.selection()
        for i in selection:
            p = self.track_pool.get_track_by_id(i)
            self.queue.remove(p)

        self.update_queuebox()
        self.queuebox_update_count()

    #function that removes first song, takes next song and calls play() on that next song
    def play_next_from_queue(self, event=None):
        self.stopSound() #stop player object
        self.remove_from_queue() #remove just played track from queue
        if self.queue: #if the queue is not empty
            self.playSound() #play first from queue
        else:
            print('queuue is empty') #if queue is empty, print that its empty

    #function to update the queueBox_count var
    def queuebox_update_count(self):
        self.queueBox_count.set(len(self.queueBox.get_children())) #takes length of list of all items in queueBox

    '''PLAYLIST FUCNTIONS'''

    #function that creats a new playlist
    def create_playlist(self, name):
        self.track_pool.create_playlist(name) #add new playlist to the track_pool
        self.playlist_window.destroy() #destroy the create playlist window

        self.update_playlistbox() #update the playlistsbox with the new playlist

        #function that adds given tracks to given playlist

    def add_tracks_to_playlist(self, playlist, tracks):
        p = self.track_pool.get_playlist_by_id(playlist) #get playlistobject
        y = [] #create empty list to add trackobjects

        #add trackobjects to y
        for i in tracks:
            y.append(self.track_pool.get_track_by_id(i))

        #add tracks to playlistobject
        p.add_tracks(y)

        self.playlist_to_current_tracklist(p) #write newly edited playlist to current tracklist
        self.track_pool.update_playlists() #update playlists.pkl
        self.update_playlistbox() #update playlistbox
        self.update_tracklistbox() #update tracklistbox

        self.add_to_playlist_window.destroy()
    #remove selected from playlist
    def remove_from_playlist(self, event=None):
        playlist = self.playlistsBox.selection()[0] #get first selected playlist
        p = self.track_pool.get_playlist_by_id(playlist) #get playlist object

        tracks = self.tracklistListBox.selection() #get selected tracks
        y = [] #empty list to get trackobjects

        for i in tracks:
            y.append(self.track_pool.get_track_by_id(i)) #append trackobj to y

        #remove tracks from playlist
        p.remove_tracks(y)

        #update everything
        self.playlist_to_current_tracklist(p)
        self.track_pool.update_playlists()
        self.update_playlistbox()
        self.update_tracklistbox()

    #function that copies entire playlist to current_tracklist
    def playlist_to_current_tracklist(self, playlist):
        self.current_tracklist.list = [] #empty current_tracklist
        for p in playlist.tracks: #for every track in playlist
            self.current_tracklist.list.append(p) #add track to current_tracklist

    def remove_playlist(self, event=None):
        p = self.playlistsBox.selection()
        x = self.track_pool.get_playlist_by_id(p[0])
        self.track_pool.playlists_list.remove(x)

        self.track_pool.update_playlists()
        self.current_tracklist.reset()
        self.update_playlistbox()
        self.update_tracklistbox()

    '''PLAYER FUNCTIONS'''
    def initialize_player(self):
        tkSnack.initializeSnack(root) #standard init process tkSnack
        self.soundObject = tkSnack.Sound() #create a SoundObject (required by tkSnack)

    #function that plays the sound
    def playSound(self, event=None):
        self.soundObject.stop()
        t = self.queue[0] #take first item from the queue

        #specify starting and ending point of the sound to be played
        self.start_value = 0
        self.end_value = -1

        self.soundObject.read(t.path) #read the sound file into the memory (soundobject)
        self.soundObject.play(start=self.start_value, end=self.end_value) #play the sound in memory from startvalue to endvalue

        #start function loop that checks whether the specified sound has finished playing
        self.check_end_song()

    #function that stops the sound
    def stopSound(self, event=None):
        self.soundObject.stop()

    #function that pauses the sound
    def pauseSound(self, event=None):
        self.soundObject.pause()

    #function that updates the volume and sets the volume in tkSnack mixer
    def update_volume(self, event=None):
        tkSnack.audio.play_gain(int(self.volumeBar.get())) #set volume in tkSnack
        self.volume.set(str(int(tkSnack.audio.play_gain())) + "%") #update volume label

    #function that checks whether the sound in memory has finished playing
    def check_end_song(self):
        # calculate total elapsedtime
        elapsed_time = tkSnack.audio.elapsedTime() + (self.start_value / self.soundObject.info()[1])

        #get length in seconds
        if self.end_value == -1: #if its played until the end
            length = self.soundObject.length(unit="SECONDS") #length = length of full sound
        else:
            length = self.end_value / self.soundObject.info()[1] #else, length is endvalue in samples / sample rate

        #if the elapsed time exceeds the length of the song
        if elapsed_time >= length:
            self.soundObject.stop() #stop playing
            self.play_next_from_queue() #play next from queue function

        #check for the end of the song every 50ms
        root.after(50, self.check_end_song)

if __name__ == "__main__":
    root = Tk() #create TK object
    app = MusicApplication(root) #create application object
    root.mainloop() #start tkinter loop

