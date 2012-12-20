#! /usr/bin/env python

from Tkinter import *
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
import tkFont
import csv
import os
import ConfigParser

from pp_medialist import MediaList
from pp_showlist import ShowList
from pp_utils import Monitor


#**************************
# Pi Presents Editor Class
# *************************

class PPEditor:


# ***************************************
# INIT
# ***************************************

    def __init__(self):


        # initialise options class and do initial reading/creation of options
        self.options=Options()

        if self.options.debug == True:
            Monitor.global_enable=True
        else:
            Monitor.global_enable=False

        self.mon=Monitor()
        self.mon.on()

        self.mon.log (self, "Pi Presents Editor is starting")

        #root is the Tkinter root widget
        self.root = tk.Tk()
        self.root.title("Editor for Pi Presents")

        self.root.configure(background='grey')
        # width, height, xoffset, yoffset
        self.root.geometry('700x300+750+000')
        # windows is 550 width
        self.root.resizable(True,True)

        #define response to main window closing
        self.root.protocol ("WM_DELETE_WINDOW", self.app_exit)

        # bind some display fields
        self.filename = tk.StringVar()
        self.display_selected_track_title = tk.StringVar()
        self.display_show = tk.StringVar()

        #Keys



# define menu
        menubar = Menu(self.root)

        profilemenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        menubar.add_cascade(label='Profile', menu = profilemenu)
        profilemenu.add_command(label='Open', command = self.open_profile)

        showmenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        showmenu.add_command(label='Remove', command = self.remove_show)
        showmenu.add_command(label='Edit', command = self.edit_show)
        menubar.add_cascade(label='Show', menu = showmenu)

        stypemenu = Menu(showmenu, tearoff=0, bg="grey", fg="black")
        stypemenu.add_command(label='Menu', command = self.add_menu)
        stypemenu.add_command(label='Mediashow', command = self.add_mediashow)
        showmenu.add_cascade(label='Add', menu = stypemenu)
        
        medialistmenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        menubar.add_cascade(label='MediaList', menu = medialistmenu)
        medialistmenu.add_command(label='Add', command = self.add_medialist)
        medialistmenu.add_command(label='Remove', command = self.remove_medialist)
      
        trackmenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        trackmenu.add_command(label='Remove', command = self.remove_track)
        trackmenu.add_command(label='Edit', command = self.edit_track)
        menubar.add_cascade(label='Track', menu = trackmenu)

        typemenu = Menu(trackmenu, tearoff=0, bg="grey", fg="black")
        typemenu.add_command(label='Video', command = self.add_video_track)
        typemenu.add_command(label='Image', command = self.add_image_track)
        typemenu.add_command(label='Message', command = self.add_message_track)
        typemenu.add_command(label='Show', command = self.add_show_track)
        typemenu.add_command(label='Menu Background', command = self.add_menu_background_track)
        typemenu.add_command(label='Child Show', command = self.add_child_show_track) 
        trackmenu.add_cascade(label='Add', menu = typemenu)

        
        optionsmenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        menubar.add_cascade(label='Options', menu = optionsmenu)
        optionsmenu.add_command(label='Edit', command = self.edit_options)

        helpmenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        menubar.add_cascade(label='Help', menu = helpmenu)
        helpmenu.add_command(label='Help', command = self.show_help)
        helpmenu.add_command(label='About', command = self.about)
         
        self.root.config(menu=menubar)

        top_frame=Frame(self.root)
        top_frame.pack(side=TOP)
        bottom_frame=Frame(self.root)
        bottom_frame.pack(side=TOP, fill=BOTH, expand=1)        


# define buttons 

        add_button = Button(top_frame, width = 15, height = 1, text='Edit Show',
                              fg='black', command = self.edit_show, bg="light grey")
        add_button.pack(side=LEFT)
        add_button = Button(top_frame, width = 15, height = 1, text='Add Image Track',
                              fg='black', command = self.add_image_track, bg="light grey")
        add_button.pack(side=LEFT)
        add_button = Button(top_frame, width = 15, height = 1, text='Add Video Track',
                              fg='black', command = self.add_video_track, bg="light grey")
        add_button.pack(side=LEFT)
        add_button = Button(top_frame, width = 15, height = 1, text='Add Message Track',
                              fg='black', command = self.add_message_track, bg="light grey")
        add_button.pack(side=LEFT)
        add_button = Button(top_frame, width = 15, height = 1, text='Edit Track',
                              fg='black', command = self.edit_track, bg="light grey")
        add_button.pack(side=LEFT)

# define display of item that is selected
        #item_name_label = Label(top_frame, width = 40, height = 1,
         #                       fg = 'black', wraplength = 300,
         #                       textvariable=self.display_selected_item, bg="white")
       # item_name_label.pack(side=LEFT,expand=1,fill=X)


        left_frame=Frame(bottom_frame, padx=5)
        left_frame.pack(side=LEFT)
        right_frame=Frame(bottom_frame,padx=5)
        right_frame.pack(side=LEFT)
        tracks_title_frame=Frame(right_frame)
        tracks_title_frame.pack(side=TOP)
        tracks_label = Label(tracks_title_frame, text="Tracks in Selected Medialist")
        tracks_label.pack()
        tracks_frame=Frame(right_frame)
        tracks_frame.pack(side=TOP)
        shows_title_frame=Frame(left_frame)
        shows_title_frame.pack(side=TOP)
        shows_label = Label(shows_title_frame, text="Shows")
        shows_label.pack()
        shows_frame=Frame(left_frame)
        shows_frame.pack(side=TOP)
        shows_title_frame=Frame(left_frame)
        shows_title_frame.pack(side=TOP)
        medialists_title_frame=Frame(left_frame)
        medialists_title_frame.pack(side=TOP)
        medialists_label = Label(medialists_title_frame, text="Medialists")
        medialists_label.pack()
        medialists_frame=Frame(left_frame)
        medialists_frame.pack(side=TOP)        
 

# define display of showlist 
        scrollbar = Scrollbar(shows_frame, orient=tk.VERTICAL)
        self.shows_display = Listbox(shows_frame, selectmode=SINGLE, height=5,
                                    width = 40, bg="white",
                                    fg="black", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.shows_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.shows_display.pack(side=LEFT, fill=BOTH, expand=1)
        self.shows_display.bind("<ButtonRelease-1>", self.e_select_show)

    
# define display of medialists
        scrollbar = Scrollbar(medialists_frame, orient=tk.VERTICAL)
        self.medialists_display = Listbox(medialists_frame, selectmode=SINGLE, height=5,
                                    width = 40, bg="white",
                                    fg="black",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.medialists_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.medialists_display.pack(side=LEFT,  fill=BOTH, expand=1)
        self.medialists_display.bind("<ButtonRelease-1>", self.select_medialist)


# define display of track
        scrollbar = Scrollbar(tracks_frame, orient=tk.VERTICAL)
        self.tracks_display = Listbox(tracks_frame, selectmode=SINGLE, height=10,
                                    width = 40, bg="white",
                                    fg="black",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tracks_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tracks_display.pack(side=LEFT,fill=BOTH, expand=1)
        self.tracks_display.bind("<ButtonRelease-1>", self.e_select_track)


# initilise variables
        self.current_medialist=None
        self.current_showlist=None
        self.current_show=None

#and display them going with Tkinter event loop
        self.root.mainloop()        


#exit
    def app_exit(self):
        self.root.destroy()
        exit()





# ***************************************
# MISCELLANEOUS
# ***************************************


    def edit_options(self):
        """edit the options then read them from file"""
        eo = OptionsDialog(self.root, self.options.options_file,'Edit Options')
        self.options.read(self.options.options_file)


    def show_help (self):
        tkMessageBox.showinfo("Help",
          " To control playing type a character\n p - pause/play\n spacebar - pause/play\n q - quit\n"
        + "+ - increase volume\n - - decrease volume\n z - tv show info\n 1 - reduce speed\n"
        + "2 - increase speed\n j - previous audio index\n k - next audio index\n i - back a chapter\n"
        + "o - forward a chapter\n n - previous subtitle index\n m - next subtitle index\n"
        + "s - toggle subtitles\n >cursor - seek forward 30\n <cursor - seek back 30\n"
        + "SHIFT >cursor - seek forward 600\n SHIFT <cursor - seek back 600\n"
        + "CTRL >cursor - next track\n CTRL <cursor - previous track")
  

    def about (self):
        tkMessageBox.showinfo("About","Editor for Pi Presents Profiles\n"
                   +"Version dated: " + datestring + "\nAuthor: Ken Thompson  - KenT")


    

# **************
# Profile
# *************

    """ opens a profile, displays the sections of showlist.json in sections pane
        clicking on a section allows it to be edited.
    """

    def open_profile(self):
        file_path=tkFileDialog.askopenfilename(initialdir=self.options.initial_profile_dir,
        		multiple=False)
        head, tail = os.path.split(file_path)
        self.profile_dir = head
        self.open_showlist(self.profile_dir)
        self.open_medialists(self.profile_dir)


# ***************************************
# Shows
# ***************************************

    def open_showlist(self,dir):      
        self.current_showlist=ShowList()
        showlist_file = dir + "/pp_showlist.json"
        if os.path.exists(showlist_file):
            self.current_showlist.open_json(showlist_file)
        else:
            self.mon.err(self,"showlist file not found at " + showlist_file)
            self.app_exit()
        self.refresh_shows_display()


    def save_showlist(self,dir):
        if self.current_showlist<>None:
            showlist_file = dir + "/pp_showlist.json"
            self.current_showlist.save_list(showlist_file)


    def add_mediashow(self):
        default_mediashow={'title': 'New Mediashow','show-ref':'mediashow-1', 'type': 'mediashow', 'medialist': '',
                          'trigger': 'start','progress': 'auto','sequence': 'ordered','repeat': 'interval','repeat-interval': '10',
                            'has-child': 'yes', 'hint-text': 'Press Return to see menu', 'hint-y': '100','hint-font': 'Helvetica 30 bold','hint-colour': 'white',
                           'transition': 'cut', 'duration': '5','omx-audio': 'hdmi','omx-other-options': ''}    
        self.add_show(default_mediashow)
        
    def add_menu(self):
        default_menu={'show-ref': 'menu-1', 'title': 'New Menu','type': 'menu','medialist': '',
                        'menu-x': '300', 'menu-y': '250', 'menu-spacing': '70','timeout': '0','has-background': 'yes',
                        'entry-font': 'Helvetica 30 bold','entry-colour': 'black', 'entry-select-colour': 'red',
                      'hint-text': 'Up, down to Select, Return to Play', 'hint-y': '100', 'hint-font': 'Helvetica 30 bold', 'hint-colour': 'white',
                       'transition': 'cut',  'duration': '5', 'omx-audio': 'hdmi','omx-other-options': ''}
        self.add_show(default_menu)

    def add_start(self):
        default_start={'title': 'First Show','show-ref':'start', 'type': 'start','start-show':'mediashow-1'}    
        self.add_show(default_start)

    def add_show(self,default):
        # append it to the showlist
        if self.current_showlist<>None:
            self.current_showlist.append(default)
            self.save_showlist(self.profile_dir)
            self.refresh_shows_display()


    def remove_show(self):
        if  self.current_showlist<>None and self.current_showlist.length()>0 and self.current_showlist.show_is_selected():
            index= self.current_showlist.selected_show_index()
            self.current_showlist.remove(index)
            self.save_showlist(self.profile_dir)
            self.refresh_shows_display()


    def refresh_shows_display(self):
        self.shows_display.delete(0,self.shows_display.size())
        for index in range(self.current_showlist.length()):
            self.shows_display.insert(END, self.current_showlist.show(index)['title'])        
        if self.current_showlist.show_is_selected():
            self.shows_display.itemconfig(self.current_showlist.selected_show_index(),fg='red')            
            
    def e_select_show(self,event):
        if self.current_showlist<>None and self.current_showlist.length()>0:
            mouse_item_index=int(event.widget.curselection()[0])
            self.current_showlist.select(mouse_item_index)
            self.refresh_shows_display()

    def e_edit_show(self,event):
        self.edit_show()

    def edit_show(self):
        show_types={'mediashow':[ 'type','title','show-ref', 'medialist','sep',
                          'trigger','progress','sequence','repeat','repeat-interval','sep',
                            'has-child', 'hint-text', 'hint-y','hint-font','hint-colour','sep',
                           'transition', 'duration','omx-audio','omx-other-options'],
                        'menu':['type','title','show-ref','medialist','sep',
                        'menu-x', 'menu-y', 'menu-spacing','timeout','has-background',
                        'entry-font','entry-colour', 'entry-select-colour','sep',
                      'hint-text', 'hint-y', 'hint-font', 'hint-colour','sep',
                       'transition','duration', 'omx-audio','omx-other-options'],
                    'start':['type','title','show-ref','start-show']
                     }
    
        field_specs={'sep':{'shape':'sep'},
                    'duration':{'param':'duration','shape':'entry','text':'Duration (secs)','must':'no','read-only':'no'},
                    'entry-font':{'param':'entry-font','shape':'entry','text':'Entry Font','must':'no','read-only':'no'},
                    'entry-colour':{'param':'entry-colour','shape':'entry','text':'Entry Colour','must':'no','read-only':'no'},
                    'entry-select-colour':{'param':'entry-select-colour','shape':'entry','text':'Selected Entry Colour','must':'no','read-only':'no'},
                    'has-child':{'param':'has-child','shape':'spinbox','text':'Has Child','must':'no','read-only':'no',
                                        'values':(' ','yes','no')},
                    'has-background':{'param':'has-background','shape':'spinbox','text':'Has Background Image','must':'no','read-only':'no',
                                      'values':(' ','yes','no')},
                    'hint-text':{'param':'hint-text','shape':'entry','text':'Hint Text','must':'no','read-only':'no'},
                    'hint-y':{'param':'hint-y','shape':'entry','text':'Hint y from bottom','must':'no','read-only':'no'},
                    'hint-font':{'param':'hint-font','shape':'entry','text':'Hint Font','must':'no','read-only':'no'},
                    'hint-colour':{'param':'hint-colour','shape':'entry','text':'Hint Colour','must':'no','read-only':'no'},
                    'medialist':{'param':'medialist','shape':'entry','text':'Medialist','must':'yes','read-only':'no'},
                    'menu-x':{'param':'menu-x','shape':'entry','text':'Menu x Position','must':'no','read-only':'no'},
                    'menu-y':{'param':'menu-y','shape':'entry','text':'Menu y Position','must':'no','read-only':'no'},
                    'menu-spacing':{'param':'menu-spacing','shape':'entry','text':'Entry Spacing','must':'no','read-only':'no'},
                    'message-font':{'param':'message-font','shape':'entry','text':'Text Font','must':'yes','read-only':'no'},
                    'message-colour':{'param':'message-colour','shape':'entry','text':'Text Colour','must':'yes','read-only':'no'},
                    'omx-audio':{'param':'omx-audio','shape':'spinbox','text':'OMX Audio','must':'no','read-only':'no',
                                       'values':(' ','hdmi','local')},
                    'omx-other-options':{'param':'omx-other-options','shape':'entry','text':'Other OMX Options','must':'no','read-only':'no'},
                    'progress':{'param':'progress','shape':'spinbox','text':'Progress','must':'no','read-only':'no',
                                        'values':(' ','auto','manual')},
                    'repeat':{'param':'repeat','shape':'spinbox','text':'Repeat','must':'no','read-only':'no',
                                        'values':(' ','oneshot','interval')},
                    'repeat-interval':{'param':'repeat-interval','shape':'entry','text':'Repeat Interval','must':'no','read-only':'no'},
                    'sequence':{'param':'sequence','shape':'spinbox','text':'Sequence','must':'no','read-only':'no',
                                        'values':(' ','ordered')},
                    'show-ref':{'param':'show-ref','shape':'entry','text':'Show Reference','must':'yes','read-only':'no'},
                    'start-show':{'param':'start-show','shape':'entry','text':'First Show','must':'no','read-only':'no'},
                    'text':{'param':'text','shape':'text','text':'Message Text','must':'no','read-only':'no'},
                    'timeout':{'param':'timeout','shape':'entry','text':'Timeout (secs)','must':'no','read-only':'no'},
                    'title':{'param':'title','shape':'entry','text':'Title','must':'yes','read-only':'no'},
                    'transition':{'param':'transition','shape':'spinbox','text':'Transition','must':'no','read-only':'no',
                                        'values':(' ','cut')},
                    'trigger':{'param':'trigger','shape':'spinbox','text':'Trigger','must':'no','read-only':'no',
                                        'values':(' ','start','button','PIR')},
                    'type':{'param':'type','shape':'entry','text':'Type','must':'yes','read-only':'yes'},
                          }

    
        if self.current_showlist<>None and self.current_showlist.show_is_selected():
            d=EditItemDialog(self.root,"Edit Show",self.current_showlist.selected_show(),show_types,field_specs)
            if d.result == True:

                self.save_showlist(self.profile_dir)
                self.refresh_shows_display()

 

# ***************************************
#   Medialists
# ***************************************

    def open_medialists(self,dir):
        self.medialists = []
        for file in os.listdir(dir):
            if file.endswith(".json") and file<>'pp_showlist.json':
                self.medialists = self.medialists + [file]
        self.medialists_display.delete(0,self.medialists_display.size())
        for index in range (len(self.medialists)):
            self.medialists_display.insert(END, self.medialists[index])


    def add_medialist(self):
        d = Edit1Dialog(self.root,"Add Medialist",
                                "File", "")
        if d != None:
            # append it to the list
            self.medialists.append(d.result)
            # add title to medialists display
            self.medialists_display.insert(END, d.result)  
            # and set it as the selected medialist
            self.refresh_medialists_display()


    def remove_medialist(index):
        pass


    def select_medialist(self,event):
        """
        user clicks on a medialst in a profile so try and select it.
        """
        # needs forgiving int for possible tkinter upgrade
        if len(self.medialists)>0:
            self.current_medialists_index=int(event.widget.curselection()[0])
            self.current_medialist=MediaList()
            self.current_medialist.open_list(self.profile_dir+ "/" + self.medialists[self.current_medialists_index])
            self.refresh_tracks_display()
            self.refresh_medialists_display()


    def refresh_medialists_display(self):
        self.medialists_display.delete(0,len(self.medialists))
        for index in range (len(self.medialists)):
            self.medialists_display.insert(END, self.medialists[index])
        if self.current_medialist<>None:
            self.medialists_display.itemconfig(self.current_medialists_index,fg='red')

    def save_medialist(self):
        self.current_medialist.save_list(self.profile_dir+ "/" + self.medialists[self.current_medialists_index])

          
# ***************************************
#   Tracks
# ***************************************
                
    def refresh_tracks_display(self):
        self.tracks_display.delete(0,self.tracks_display.size())
        for index in range(self.current_medialist.length()):
            self.tracks_display.insert(END, self.current_medialist.track(index)['title'])        
        if self.current_medialist.track_is_selected():
            self.tracks_display.itemconfig(self.current_medialist.selected_track_index(),fg='red')            

            
    def e_select_track(self,event):
        if self.current_medialist<>None and self.current_medialist.length()>0:
            mouse_item_index=int(event.widget.curselection()[0])
            self.current_medialist.select(mouse_item_index)
            self.refresh_tracks_display()

    def e_edit_track(self,event):
        self.edit_track()

    def edit_track(self):
        track_types={'video':['type','title','track-ref','location','omx-audio'],
                        'message':['type','title','track-ref','text','duration','message-font','message-colour'],
                         'show':['type','title','track-ref','sub-show'],
                         'image':['type','title','track-ref','location','duration','transition'],
                        'menu-background':['type','title','track-ref','location']
             }
    
        field_specs={'sep':{'shape':'sep'},
                            'duration':{'param':'duration','shape':'entry','text':'Duration (secs)','must':'no','read-only':'no'},
                            'location':{'param':'location','shape':'browse','text':'Location','must':'yes','read-only':'no'},
                            'message-font':{'param':'message-font','shape':'entry','text':'Text Font','must':'yes','read-only':'no'},
                            'message-colour':{'param':'message-colour','shape':'entry','text':'Text Colour','must':'yes','read-only':'no'},
                            'omx-audio':{'param':'omx-audio','shape':'spinbox','text':'omx-audio','must':'no','read-only':'no',
                                       'values':(' ','hdmi','local')},
                            'show-ref':{'param':'show-ref','shape':'entry','text':'Show Reference','must':'yes','read-only':'no'},
                            'sub-show':{'param':'sub-show','shape':'entry','text':'Show to Run','must':'no','read-only':'no'},
                            'text':{'param':'text','shape':'text','text':'Message Text','must':'no','read-only':'no'},
                            'title':{'param':'title','shape':'entry','text':'Title','must':'yes','read-only':'no'},
                            'track-ref':{'param':'track-ref','shape':'entry','text':'Track Reference','must':'no','read-only':'no'},
                            'transition':{'param':'transition','shape':'spinbox','text':'Transition','must':'no','read-only':'no',
                                        'values':(' ','cut')},
                            'type':{'param':'type','shape':'entry','text':'Type','must':'yes','read-only':'yes'}
                          }

    
        if self.current_medialist<>None and self.current_medialist.track_is_selected():
            d=EditItemDialog(self.root,"Edit Track",self.current_medialist.selected_track(),track_types,field_specs)
            if d.result == True:
                self.save_medialist()
            self.refresh_tracks_display()


    def add_track(self,default):
        if self.current_medialist<>None:
            self.current_medialist.append(default)
            self.current_medialist.select(self.current_medialist.length()-1)
            self.save_medialist()
            self.refresh_tracks_display()


    def add_message_track(self):
        default_message={'title':'New Message','track-ref':'','type':'message','text':'','duration':'5','message-font':'Helvetica 30 bold','message-colour':'white'}
        self.add_track(default_message)
                       
    def add_video_track(self):
        default_video={'title':'New Video','track-ref':'','type':'video','location':'','omx-audio':''}
        self.add_track(default_video)
    
    def add_image_track(self):
        default_image={'title':'New Image','track-ref':'','type':'image','location':'','duration':'5','transition':'cut'}
        self.add_track(default_image)
    
    def add_show_track(self):
        default_show={'title':'New Show','track-ref':'','type':'show','sub-show':''}
        self.add_track(default_show)
        
    def add_menu_background_track(self):
        default_menu_background={'title':'New Menu Background','track-ref':'pp-menu-background','type':'menu-background','location':''}
        self.add_track(default_menu_background)

    def add_child_show_track(self):
        default_show={'title':'New Child Show','track-ref':'pp-child-show','type':'show','sub-show':''}
        self.add_track(default_show)

    def remove_track(self):
        if  self.current_medialist<>None and self.current_medialist.length()>0 and self.current_medialist.track_is_selected():
            index= self.current_medialist.selected_track_index()
            self.current_medialist.remove(index)
            self.save_medialist()
            self.refresh_tracks_display()


# ***************************************
# OLD
# ***************************************



    def add_relative(self):                                
        """
        Opens a dialog box to open a file,
        then stores the  track in the playlist.
        """
        # get the file
        self.filename.set(tkFileDialog.askopenfilename(initialdir=self.options.initial_track_dir,
			multiple=False))

        self.file = self.filename.get()
        if self.file=="":
            return
        # split it to use leaf as the initial title
        self.file_pieces = self.file.split("/")
        
        # append it to the playlist
        self.playlist.append([self.file, self.file_pieces[-1],'',''])
        # add title to playlist display
        self.track_titles_display.insert(END, self.file_pieces[-1])
        
        # and set it as the selected track
        self.playlist.select(self.playlist.length()-1)
        self.display_selected_track(self.playlist.selected_track_index())
        

    def add_absolute(self):
        d = EditTrackDialog(self.root,"Add URL",
                                "Location", "",
                                "Title", "")
        if d.result != None:
            # append it to the playlist
            self.playlist.append(d.result)
            # add title to playlist display
            self.track_titles_display.insert(END, d.result[1])  
            # and set it as the selected track
            self.playlist.select(self.playlist.length()-1)
            self.display_selected_track(self.playlist.selected_track_index())
   
 
# *************************************
# EDIT 1 DIALOG CLASS
# ************************************

class Edit1Dialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title, label, default):
        #save the extra args to instance variables
        self.label_1 = label
        self.default_1 = default     
        #and call the base class _init_which uses the args in body
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, master):
        Label(master, text=self.label_1).grid(row=0)
        self.field1 = Entry(master)
        self.field1.grid(row=0, column=1)
        self.field1.insert(0,self.default_1)
        return self.field1 # initial focus on title


    def apply(self):
        self.result= self.field1.get()
        return self.result



# ***************************************
# pp_editor OPTIONS CLASS
# ***************************************

class Options:

# store associated with the object is the disc file. Variables used by the player
# is just a cached interface.
# options dialog class is a second class that reads and saves the otions from the options file

    def __init__(self):

        # define options for Editor
        self.initial_profile_dir =""   #initial directory for add track.
        self.initial_media_dir =""   #initial directory for open playlist      
        self.debug = False  # print debug information to terminal


    # create an options file if necessary
        self.options_file = 'pp_editor.cfg'
        if os.path.exists(self.options_file):
            self.read(self.options_file)
        else:
            self.create(self.options_file)
            self.read(self.options_file)

    
    def read(self,file_name):
        """reads options from options file to interface"""
        config=ConfigParser.ConfigParser()
        config.read(file_name)
        
        self.initial_profile_dir =config.get('config','profile',0)
        self.initial_media_dir =config.get('config','media',0)    

        if config.get('config','debug',0) == 'on':
            self.debug  =True
        else:
            self.debug=False

     
    def create(self,file_name):
        config=ConfigParser.ConfigParser()
        config.add_section('config')
        config.set('config','profile','')
        config.set('config','media','')
        config.set('config','debug','off')
        with open(file_name, 'wb') as config_file:
            config.write(config_file)



# *************************************
# PP_EDITOR OPTIONS DIALOG CLASS
# ************************************

class OptionsDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, options_file, title=None, ):
        # instantiate the subclass attributes
        self.options_file=options_file

        # init the super class
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, master):

        config=ConfigParser.ConfigParser()
        config.read(self.options_file)

        Label(master, text="").grid(row=20, sticky=W)
        Label(master, text="Initial directory for profiles:").grid(row=21, sticky=W)
        self.e_profile = Entry(master)
        self.e_profile.grid(row=22)
        self.e_profile.insert(0,config.get('config','profile',0))

        Label(master, text="").grid(row=30, sticky=W)
        Label(master, text="Inital directory for media:").grid(row=31, sticky=W)
        self.e_media = Entry(master)
        self.e_media.grid(row=32)
        self.e_media.insert(0,config.get('config','media',0))

        self.debug_var = StringVar()
        self.cb_debug = Checkbutton(master,text="Debug Editor",variable=self.debug_var, onvalue="on",offvalue="off")
        self.cb_debug.grid(row=50,columnspan=2, sticky = W)
        if config.get('config','debug',0)=="on":
            self.cb_debug.select()
        else:
            self.cb_debug.deselect()

        return None    # no initial focus

    def apply(self):
        self.save_options()
        return True

    def save_options(self):
        """ save the output of the options edit dialog to file"""
        config=ConfigParser.ConfigParser()
        config.add_section('config')
        config.set('config','profile',self.e_profile.get())
        config.set('config','media',self.e_media.get())
        config.set('config','debug',self.debug_var.get())
        with open(self.options_file, 'wb') as optionsfile:
            config.write(optionsfile)
    


# *************************************
# EDIT SHOW AND TRACK CONTENT
# ************************************

class EditItemDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title, tp, track_types,field_specs):
        self.mon=Monitor()
        self.mon.on()
        #save the extra arg to instance variable
        self.tp = tp   # dictionary - the track parameters to be edited
        self.track_types= track_types
        self.field_specs=field_specs

        #and call the base class _init_which calls body immeadiately and apply on OK pressed
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, master):
                    
        # get fields for this type of track               }
        track_fields=self.track_types[self.tp['type']]              
        # populate the dialog box
        row=0
        self.fields=[]
        for field in track_fields:
            obj=self.make_entry(master,self.field_specs[field],row)
            if obj<>None: self.fields.append(obj)
            row +=1
        return None # No initial focus


    def buttonbox(self):
        '''add standard button box.
        override to get rid of key bindings whihc cause trouble with text widget
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        #self.bind("<Return>", self.ok)
        #self.bind("<Escape>", self.cancel)

        box.pack()

    # create an entry in a dialog box
    def make_entry(self,master,field,row):
        if field['shape']=="sep":
            Label(master,text='',width=30, anchor=W).grid(row=row,sticky=W)
            return None
        else:
            if field['must']=='yes':
                bg='pink'
            else:
                bg='white'
            Label(master,text=field['text'],width=22, anchor=W).grid(row=row,sticky=W)
            if field['shape']=="entry":
                obj=Entry(master,bg=bg,width=40)
            elif field['shape']=="text":
                obj=Text(master,bg=bg,width=40,height=4)
            elif field['shape']=='spinbox':
                obj=Spinbox(master,bg=bg,width=40,values=field['values'])                          
            elif field['shape']=="browse":
                obj=Entry(master,bg=bg,width=40)
            obj.grid(row=row,column=1,sticky=W)
            parameter=field['param']
            if parameter in self.tp:
                obj.insert(END,self.tp[field['param']])
            else:
                self.mon.log(self,"Valuse for field not found in opened file: " + parameter)
            if field['read-only']=='yes':
                obj.config(state="readonly")
            return obj


    def apply(self):
        track_fields=self.track_types[self.tp['type']]
        row=0
        for field in track_fields:
            field_spec=self.field_specs[field]
            if field_spec['shape']<>'sep':
                if field_spec['shape']=='text':
                    self.tp[field_spec['param']]=self.fields[row].get(1.0,END)
                else:
                    self.tp[field_spec['param']]=self.fields[row].get().strip()
                row +=1
        self.result=True
        return self.result




# ***************************************
# MAIN
# ***************************************


if __name__ == "__main__":
    datestring=" 20 Nov 2012"
    editor = PPEditor()

