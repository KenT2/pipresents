
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
import shutil

from pp_medialist import MediaList
from pp_showlist import ShowList
from pp_utils import Monitor
from pp_options import ed_options

#**************************
# Pi Presents Editor Class
# *************************

class PPEditor:

    IMAGE_FILES=('Image files', '.gif','.jpg','.jpeg','.bmp','.png','.tif')
    VIDEO_FILES=('video files','.mp4','.mkv','.avi','.mp2','.wmv')
    AUDIO_FILES=('audio files','.mp3')

# ***************************************
# INIT
# ***************************************

    def __init__(self):

        self.command_options=ed_options()
        
        # where am I?
        if self.command_options['code']=="":
            pp_dir="/home/pi/pipresents"
        else:
            pp_dir=self.command_options['code']
            
        if not os.path.exists(pp_dir+"/pp_editor.py"):
            tkMessageBox.showwarning("Pi Presents","Bad Application Directory")
            exit()
            
        #Initialise logging
        Monitor.log_path=pp_dir
        self.mon=Monitor()
        self.mon.on()

        if self.command_options['debug'] == True:
            Monitor.global_enable=True
        else:
            Monitor.global_enable=False

        self.mon.log (self, "Pi Presents Editor is starting")

 
        #root is the Tkinter root widget
        self.root = tk.Tk()
        self.root.title("Editor for Pi Presents")

        self.root.configure(background='grey')
        # width, height, xoffset, yoffset
        self.root.geometry('900x300+650+000')
        # windows is 700 width
        self.root.resizable(True,True)

        #define response to main window closing
        self.root.protocol ("WM_DELETE_WINDOW", self.app_exit)

        # bind some display fields
        self.filename = tk.StringVar()
        self.display_selected_track_title = tk.StringVar()
        self.display_show = tk.StringVar()


# define menu
        menubar = Menu(self.root)

        profilemenu = Menu(menubar, tearoff=0, bg="grey", fg="black")
        profilemenu.add_command(label='Open', command = self.open_existing_profile)
        
        menubar.add_cascade(label='Profile', menu = profilemenu)

        ptypemenu = Menu(profilemenu, tearoff=0, bg="grey", fg="black")
        ptypemenu.add_command(label='Exhibit', command = self.new_exhibit_profile)
        ptypemenu.add_command(label='Media Show', command = self.new_mediashow_profile)
        ptypemenu.add_command(label='Menu', command = self.new_menu_profile)
        ptypemenu.add_command(label='Presentation', command = self.new_presentation_profile)
        ptypemenu.add_command(label='Interactive', command = self.new_interactive_profile)
        ptypemenu.add_command(label='Blank', command = self.new_blank_profile)
        profilemenu.add_cascade(label='New from Template', menu = ptypemenu)
        
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
        trackmenu.add_command(label='Add from Dir', command = self.add_tracks_from_dir)
        trackmenu.add_command(label='Add from File', command = self.add_track_from_file)


        menubar.add_cascade(label='Track', menu = trackmenu)

        typemenu = Menu(trackmenu, tearoff=0, bg="grey", fg="black")
        typemenu.add_command(label='Video', command = self.new_video_track)
        typemenu.add_command(label='Image', command = self.new_image_track)
        typemenu.add_command(label='Message', command = self.new_message_track)
        typemenu.add_command(label='Show', command = self.new_show_track)
        typemenu.add_command(label='Menu Background', command = self.new_menu_background_track)
        typemenu.add_command(label='Child Show', command = self.new_child_show_track) 
        trackmenu.add_cascade(label='New', menu = typemenu)

        
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

        left_frame=Frame(bottom_frame, padx=5)
        left_frame.pack(side=LEFT)
        middle_frame=Frame(bottom_frame,padx=5)
        middle_frame.pack(side=LEFT)              
        right_frame=Frame(bottom_frame,padx=5)
        right_frame.pack(side=LEFT)
        updown_frame=Frame(bottom_frame,padx=5)
        updown_frame.pack(side=LEFT)
        
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
        
 # define buttons 

        add_button = Button(middle_frame, width = 5, height = 1, text='Edit',
                              fg='black', command = self.edit_show, bg="light grey")
        add_button.pack(side=TOP)
        add_button = Button(updown_frame, width = 5, height = 1, text='Add',
                              fg='black', command = self.add_track_from_file, bg="light grey")
        add_button.pack(side=TOP)
        add_button = Button(updown_frame, width = 5, height = 1, text='Edit',
                              fg='black', command = self.edit_track, bg="light grey")
        add_button.pack(side=TOP)
        add_button = Button(updown_frame, width = 5, height = 1, text='Up',
                              fg='black', command = self.move_track_up, bg="light grey")
        add_button.pack(side=TOP)
        add_button = Button(updown_frame, width = 5, height = 1, text='Down',
                              fg='black', command = self.move_track_down, bg="light grey")
        add_button.pack(side=TOP)



# define display of showlist 
        scrollbar = Scrollbar(shows_frame, orient=tk.VERTICAL)
        self.shows_display = Listbox(shows_frame, selectmode=SINGLE, height=5,
                                    width = 40, bg="white",activestyle=NONE,
                                    fg="black", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.shows_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.shows_display.pack(side=LEFT, fill=BOTH, expand=1)
        self.shows_display.bind("<ButtonRelease-1>", self.e_select_show)

    
# define display of medialists
        scrollbar = Scrollbar(medialists_frame, orient=tk.VERTICAL)
        self.medialists_display = Listbox(medialists_frame, selectmode=SINGLE, height=5,
                                    width = 40, bg="white",activestyle=NONE,
                                    fg="black",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.medialists_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.medialists_display.pack(side=LEFT,  fill=BOTH, expand=1)
        self.medialists_display.bind("<ButtonRelease-1>", self.select_medialist)


# define display of track
        scrollbar = Scrollbar(tracks_frame, orient=tk.VERTICAL)
        self.tracks_display = Listbox(tracks_frame, selectmode=SINGLE, height=15,
                                    width = 40, bg="white",activestyle=NONE,
                                    fg="black",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tracks_display.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tracks_display.pack(side=LEFT,fill=BOTH, expand=1)
        self.tracks_display.bind("<ButtonRelease-1>", self.e_select_track)


# initialise variables

       # initialise editor options class and do initial reading/creation of options
        self.options=Options() #creates options file if necessary
        self.init()
        


#and display them going with Tkinter event loop
        self.root.mainloop()        


#exit
    def app_exit(self):
        self.root.destroy()
        exit()


    def init(self):
        self.options.read()
        self.pp_home_dir = self.options.pp_home_dir
        self.initial_media_dir = self.options.initial_media_dir
        self.mon.log(self,"Data Home is "+self.pp_home_dir)
        self.mon.log(self,"Initial Media is "+self.initial_media_dir)
        self.current_medialist=None
        self.current_showlist=None
        self.current_show=None
        self.shows_display.delete(0,END)
        self.medialists_display.delete(0,END)
        self.tracks_display.delete(0,END)



# ***************************************
# MISCELLANEOUS
# ***************************************


    def edit_options(self):
        """edit the options then read them from file"""
        eo = OptionsDialog(self.root, self.options.options_file,'Edit Options')
        if eo.result==True: self.init()


    def show_help (self):
        tkMessageBox.showinfo("Help",
       "Read manual.pdf")
  

    def about (self):
        tkMessageBox.showinfo("About","Editor for Pi Presents Profiles\n"
                   +"Version dated: " + datestring + "\nAuthor: Ken Thompson  - KenT")


    

# **************
# Profile
# *************

    """ opens a profile, displays the sections of showlist.json in sections pane
        clicking on a section allows it to be edited.
    """

    def open_existing_profile(self):
        initial_dir=self.pp_home_dir+os.sep+"pp_profiles"
        dir_path=tkFileDialog.askdirectory(initialdir=initial_dir)
        if dir_path<>"":
            self.open_profile(dir_path)
        

    def open_profile(self,dir_path):
        showlist_file = dir_path + os.sep + "pp_showlist.json"
        if os.path.exists(showlist_file)==False:
            self.mon.err(self,"Not a Profile: " + dir_path + "\n\nHint: Have you clicked in the profile directory?")
            return
        self.pp_profile_dir = dir_path
        self.root.title("Editor for Pi Presents - "+ self.pp_profile_dir)
        self.open_showlist(self.pp_profile_dir)
        self.open_medialists(self.pp_profile_dir)
        self.refresh_tracks_display()


    def new_profile(self,profile):
        d = Edit1Dialog(self.root,"New Profile","Name", "")
        if d != None:
            name=str(d.result)
            to = self.pp_home_dir + os.sep + "pp_profiles"+ os.sep + name
            if os.path.exists(to)== False:
                shutil.copytree(profile, to, symlinks=False, ignore=None)
                self.open_profile(to)
            else:
                tkMessageBox.showwarning(
                                "New Profile",
                                "Profile exists\n(%s)" % to
                                        )
        


    def new_exhibit_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_exhibit"
        self.new_profile(profile)

    def new_interactive_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_interactive"
        self.new_profile(profile)

    def new_menu_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_menu"
        self.new_profile(profile)

    def new_presentation_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_presentation"
        self.new_profile(profile)

    def new_blank_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_blank"
        self.new_profile(profile)

    def new_mediashow_profile(self):
        profile = os.getcwd()+"/pp_home/pp_profiles/ppt_mediashow"
        self.new_profile(profile)

# ***************************************
# Shows
# ***************************************

    def open_showlist(self,dir):
        showlist_file = dir + os.sep + "pp_showlist.json"
        if os.path.exists(showlist_file)==False:
            self.mon.err(self,"showlist file not found at " + dir + "\n\nHint: Have you clicked in the profile directory?")
            self.app_exit()
        self.current_showlist=ShowList()
        self.current_showlist.open_json(showlist_file)
        self.refresh_shows_display()


    def save_showlist(self,dir):
        if self.current_showlist<>None:
            showlist_file = dir + os.sep + "pp_showlist.json"
            self.current_showlist.save_list(showlist_file)


    def add_mediashow(self):
        default_mediashow={'title': 'New Mediashow','show-ref':'', 'type': 'mediashow', 'medialist': '',
                          'trigger': 'start','progress': 'auto','sequence': 'ordered','repeat': 'interval','repeat-interval': '10',
                            'has-child': 'no', 'hint-text': '', 'hint-y': '100','hint-font': 'Helvetica 30 bold','hint-colour': 'white',
                           'transition': 'cut', 'duration': '5','omx-audio': 'hdmi','omx-other-options': ''}    
        self.add_show(default_mediashow)
        
    def add_menu(self):
        default_menu={'show-ref': '', 'title': 'New Menu','type': 'menu','medialist': '',
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
            self.save_showlist(self.pp_profile_dir)
            self.refresh_shows_display()


    def remove_show(self):
        if  self.current_showlist<>None and self.current_showlist.length()>0 and self.current_showlist.show_is_selected():
            index= self.current_showlist.selected_show_index()
            self.current_showlist.remove(index)
            self.save_showlist(self.pp_profile_dir)
            self.refresh_shows_display()

    def show_refs(self):
        _show_refs=[]
        for index in range(self.current_showlist.length()):
            if self.current_showlist.show(index)['show-ref']<>"start":
                _show_refs.append(self.current_showlist.show(index)['show-ref'])
        return _show_refs
 
    def refresh_shows_display(self):
        self.shows_display.delete(0,self.shows_display.size())
        for index in range(self.current_showlist.length()):
            self.shows_display.insert(END, self.current_showlist.show(index)['title']+"   ["+self.current_showlist.show(index)['show-ref']+"]")        
        if self.current_showlist.show_is_selected():
            self.shows_display.itemconfig(self.current_showlist.selected_show_index(),fg='red')            
            self.shows_display.see(self.current_showlist.selected_show_index())

            
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
                    'has-child':{'param':'has-child','shape':'option-menu','text':'Has Child','must':'no','read-only':'no',
                                        'values':['yes','no']},
                    'has-background':{'param':'has-background','shape':'option-menu','text':'Has Background Image','must':'no','read-only':'no',
                                      'values':['yes','no']},
                    'hint-text':{'param':'hint-text','shape':'entry','text':'Hint Text','must':'no','read-only':'no'},
                    'hint-y':{'param':'hint-y','shape':'entry','text':'Hint y from bottom','must':'no','read-only':'no'},
                    'hint-font':{'param':'hint-font','shape':'entry','text':'Hint Font','must':'no','read-only':'no'},
                    'hint-colour':{'param':'hint-colour','shape':'entry','text':'Hint Colour','must':'no','read-only':'no'},
                    'medialist':{'param':'medialist','shape':'entry','text':'Medialist','must':'no','read-only':'no'},
                    'menu-x':{'param':'menu-x','shape':'entry','text':'Menu x Position','must':'no','read-only':'no'},
                    'menu-y':{'param':'menu-y','shape':'entry','text':'Menu y Position','must':'no','read-only':'no'},
                    'menu-spacing':{'param':'menu-spacing','shape':'entry','text':'Entry Spacing','must':'no','read-only':'no'},
                    'message-font':{'param':'message-font','shape':'entry','text':'Text Font','must':'yes','read-only':'no'},
                    'message-colour':{'param':'message-colour','shape':'entry','text':'Text Colour','must':'yes','read-only':'no'},
                    'omx-audio':{'param':'omx-audio','shape':'option-menu','text':'OMX Audio','must':'no','read-only':'no',
                                       'values':['hdmi','local']},
                    'omx-other-options':{'param':'omx-other-options','shape':'entry','text':'Other OMX Options','must':'no','read-only':'no'},
                    'progress':{'param':'progress','shape':'option-menu','text':'Progress','must':'no','read-only':'no',
                                        'values':['auto','manual']},
                    'repeat':{'param':'repeat','shape':'option-menu','text':'Repeat','must':'no','read-only':'no',
                                        'values':['oneshot','interval']},
                    'repeat-interval':{'param':'repeat-interval','shape':'entry','text':'Repeat Interval (secs.)','must':'no','read-only':'no'},
                    'sequence':{'param':'sequence','shape':'option-menu','text':'Sequence','must':'no','read-only':'no',
                                        'values':['ordered',]},
                    'show-ref':{'param':'show-ref','shape':'entry','text':'Show Reference','must':'no','read-only':'no'},
                    'start-show':{'param':'start-show','shape':'option-menu','text':'First Show','must':'no','read-only':'no'},
                    'text':{'param':'text','shape':'text','text':'Message Text','must':'no','read-only':'no'},
                    'timeout':{'param':'timeout','shape':'entry','text':'Timeout (secs)','must':'no','read-only':'no'},
                    'title':{'param':'title','shape':'entry','text':'Title','must':'no','read-only':'no'},
                    'transition':{'param':'transition','shape':'option-menu','text':'Transition','must':'no','read-only':'no',
                                        'values':['cut',]},
                    'trigger':{'param':'trigger','shape':'option-menu','text':'Trigger','must':'no','read-only':'no',
                                        'values':['start','button','PIR']},
                    'type':{'param':'type','shape':'entry','text':'Type','must':'no','read-only':'yes'},
                          }

    
        if self.current_showlist<>None and self.current_showlist.show_is_selected():
            d=EditItemDialog(self.root,"Edit Show",self.current_showlist.selected_show(),show_types,field_specs,self.show_refs())
            if d.result == True:

                self.save_showlist(self.pp_profile_dir)
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
        self.current_medialists_index=-1
        self.current_medialist=None


    def add_medialist(self):
        d = Edit1Dialog(self.root,"Add Medialist",
                                "File", "")
        if d != None:
            name=str(d.result)
            if not name.endswith(".json"):
                name=name+(".json")
            path = self.pp_profile_dir + os.sep + name
            if os.path.exists(path)== False:
                nfile = open(path,'wb')
                nfile.write("{")
                nfile.write("\"tracks\": [")
                nfile.write("]")
                nfile.write("}")
                nfile.close()
                # append it to the list
                self.medialists.append(name)
                # add title to medialists display
                self.medialists_display.insert(END, name)  
                # and set it as the selected medialist
                self.refresh_medialists_display()
            else:
                tkMessageBox.showwarning(
                                "Add medialist",
                                "Medialist file exists\n(%s)" % path
                                        )
                        


    def remove_medialist(self):
        if self.current_medialist<>None:
            if tkMessageBox.askokcancel("Delete Medialist","Delete Medialist"):
                os.remove(self.pp_profile_dir+ os.sep + self.medialists[self.current_medialists_index])
                self.open_medialists(self.pp_profile_dir)
                self.refresh_medialists_display()
                self.refresh_tracks_display()


    def select_medialist(self,event):
        """
        user clicks on a medialst in a profile so try and select it.
        """
        # needs forgiving int for possible tkinter upgrade
        if len(self.medialists)>0:
            self.current_medialists_index=int(event.widget.curselection()[0])
            self.current_medialist=MediaList()
            self.current_medialist.open_list(self.pp_profile_dir+ os.sep + self.medialists[self.current_medialists_index])
            self.refresh_tracks_display()
            self.refresh_medialists_display()


    def refresh_medialists_display(self):
        self.medialists_display.delete(0,len(self.medialists))
        for index in range (len(self.medialists)):
            self.medialists_display.insert(END, self.medialists[index])
        if self.current_medialist<>None:
            self.medialists_display.itemconfig(self.current_medialists_index,fg='red')
            self.medialists_display.see(self.current_medialists_index)

    def save_medialist(self):
        self.current_medialist.save_list(self.pp_profile_dir+ os.sep + self.medialists[self.current_medialists_index])

          
# ***************************************
#   Tracks
# ***************************************
                
    def refresh_tracks_display(self):
        self.tracks_display.delete(0,self.tracks_display.size())
        if self.current_medialist<>None:
            for index in range(self.current_medialist.length()):
                if self.current_medialist.track(index)['track-ref']<>"":
                    track_ref_string="  ["+self.current_medialist.track(index)['track-ref']+"]"
                else:
                    track_ref_string=""
                self.tracks_display.insert(END, self.current_medialist.track(index)['title']+track_ref_string)        
            if self.current_medialist.track_is_selected():
                self.tracks_display.itemconfig(self.current_medialist.selected_track_index(),fg='red')            
                self.tracks_display.see(self.current_medialist.selected_track_index())
            
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
                            'location':{'param':'location','shape':'browse','text':'Location','must':'no','read-only':'no'},
                            'message-font':{'param':'message-font','shape':'entry','text':'Text Font','must':'no','read-only':'no'},
                            'message-colour':{'param':'message-colour','shape':'entry','text':'Text Colour','must':'no','read-only':'no'},
                            'omx-audio':{'param':'omx-audio','shape':'option-menu','text':'omx-audio','must':'no','read-only':'no',
                                       'values':['hdmi','local','']},
                            'show-ref':{'param':'show-ref','shape':'entry','text':'Show Reference','must':'no','read-only':'no'},
                            'sub-show':{'param':'sub-show','shape':'option-menu','text':'Show to Run','must':'no','read-only':'no'},
                            'text':{'param':'text','shape':'text','text':'Message Text','must':'no','read-only':'no'},
                            'title':{'param':'title','shape':'entry','text':'Title','must':'no','read-only':'no'},
                            'track-ref':{'param':'track-ref','shape':'entry','text':'Track Reference','must':'no','read-only':'no'},
                            'transition':{'param':'transition','shape':'option-menu','text':'Transition','must':'no','read-only':'no',
                                        'values':['cut','']},
                            'type':{'param':'type','shape':'entry','text':'Type','must':'no','read-only':'yes'}
                          }

    
        if self.current_medialist<>None and self.current_medialist.track_is_selected():
            d=EditItemDialog(self.root,"Edit Track",self.current_medialist.selected_track(),track_types,field_specs,self.show_refs())
            if d.result == True:
                self.save_medialist()
            self.refresh_tracks_display()

    def move_track_up(self):
        if self.current_medialist<>None and self.current_medialist.track_is_selected():
            self.current_medialist.move_up()
            self.refresh_tracks_display()
            self.save_medialist()

    def move_track_down(self):
        if self.current_medialist<>None and self.current_medialist.track_is_selected():
            self.current_medialist.move_down()
            self.refresh_tracks_display()
            self.save_medialist()
        
    def new_track(self,default):
        if self.current_medialist<>None:
            self.current_medialist.append(default)
            self.current_medialist.select(self.current_medialist.length()-1)
            self.save_medialist()
            self.refresh_tracks_display()


    def new_message_track(self):
        default_message={'title':'New Message','track-ref':'','type':'message','text':'','duration':'5','message-font':'Helvetica 30 bold','message-colour':'white'}
        self.new_track(default_message)
                       
    def new_video_track(self):
        default_video={'title':'New Video','track-ref':'','type':'video','location':'','omx-audio':''}
        self.new_track(default_video)
    
    def new_image_track(self):
        default_image={'title':'New Image','track-ref':'','type':'image','location':'','duration':'5','transition':'cut'}
        self.new_track(default_image)
    
    def new_show_track(self):
        default_show={'title':'New Show','track-ref':'','type':'show','sub-show':''}
        self.new_track(default_show)
        
    def new_menu_background_track(self):
        default_menu_background={'title':'New Menu Background','track-ref':'pp-menu-background','type':'menu-background','location':''}
        self.new_track(default_menu_background)

    def new_child_show_track(self):
        default_show={'title':'New Child Show','track-ref':'pp-child-show','type':'show','sub-show':''}
        self.new_track(default_show)

    def remove_track(self):
        if  self.current_medialist<>None and self.current_medialist.length()>0 and self.current_medialist.track_is_selected():
            if tkMessageBox.askokcancel("Delete Track","Delete Track"):
                index= self.current_medialist.selected_track_index()
                self.current_medialist.remove(index)
                self.save_medialist()
                self.refresh_tracks_display()
                
    def add_track_from_file(self):
        if self.current_medialist==None: return
        files_path=tkFileDialog.askopenfilename(initialdir=self.options.initial_media_dir,
        		multiple=True)
        # fix for tkinter bug
        files_path =  self.root.tk.splitlist(files_path)
        for file_path in files_path:
            self.add_track(file_path)

    def add_tracks_from_dir(self):
        if self.current_medialist==None: return
        image_specs =[
            PPEditor.IMAGE_FILES,
            PPEditor.VIDEO_FILES,
            PPEditor.AUDIO_FILES,
          ('All files', '*')]    #last one is ignored in finding files
                                    # in directory, for dialog box only
        directory=tkFileDialog.askdirectory(initialdir=self.options.initial_media_dir)

        #print image_specs
        # make list of exts we recognise
        exts = []
        for image_spec in image_specs[:-1]:
            image_list=image_spec[1:]
            for ext in image_list:
                exts.append(ext)
        #list of files in directory matching exts
        files=[]
        for file in os.listdir(directory):
            file = directory + os.sep + file
            (root_file,ext_file)= os.path.splitext(file)
            if ext_file.lower() in exts:
                files.append(file)
        #now add to medialist from the files
        for afile in files:
            self.add_track(afile)



    def add_track(self,afile):
        relpath = os.path.relpath(afile,self.pp_home_dir)
        common = os.path.commonprefix([afile,self.pp_home_dir])
        if common.endswith("pp_home") == False:
            location = afile
        else:
            location = "+" + os.sep + relpath
        (root,title)=os.path.split(afile)
        (root,ext)= os.path.splitext(afile)
        if ext.lower() in PPEditor.IMAGE_FILES:
            image={'title':title,'track-ref':'','type':'image','location':location,'duration':'5','transition':'cut'}
            self.new_track(image)
        elif ext.lower() in PPEditor.VIDEO_FILES:
            video={'title':title,'track-ref':'','type':'video','location':location,'omx-audio':''}
            self.new_track(video)
        elif ext.lower() in PPEditor.AUDIO_FILES:
            video={'title':title,'track-ref':'','type':'video','location':location,'omx-audio':''}
            self.new_track(video)
        else:
            self.mon.err(self,afile + " - file extension not recognised")

 
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
# options dialog class is a second class that reads and saves the options from the options file

    def __init__(self):

        # define options for Editor
        self.pp_home_dir =""   #home directory containing profile to be edited.
        self.initial_media_dir =""   #initial directory for open playlist      
        self.debug = False  # print debug information to terminal


    # create an options file if necessary
        self.options_file = 'pp_editor.cfg'
        if not os.path.exists(self.options_file):
            self.create()


    
    def read(self):
        """reads options from options file to interface"""
        config=ConfigParser.ConfigParser()
        config.read(self.options_file)
        
        self.pp_home_dir =config.get('config','home',0)
        self.initial_media_dir =config.get('config','media',0)    

    def create(self):
        config=ConfigParser.ConfigParser()
        config.add_section('config')
        config.set('config','home','/home/pi/pp_home')
        config.set('config','media','/home/pi')
        with open(self.options_file, 'wb') as config_file:
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
        self.result=False
        config=ConfigParser.ConfigParser()
        config.read(self.options_file)

        Label(master, text="").grid(row=20, sticky=W)
        Label(master, text="Pi Presents Data Home:").grid(row=21, sticky=W)
        self.e_home = Entry(master,width=80)
        self.e_home.grid(row=22)
        self.e_home.insert(0,config.get('config','home',0))

        Label(master, text="").grid(row=30, sticky=W)
        Label(master, text="Inital directory for media:").grid(row=31, sticky=W)
        self.e_media = Entry(master,width=80)
        self.e_media.grid(row=32)
        self.e_media.insert(0,config.get('config','media',0))

        return None    # no initial focus

    def validate(self):
        if os.path.exists(self.e_home.get())== False:
            tkMessageBox.showwarning("Pi Presents Editor","Data Home not found")
            return 0
        if os.path.exists(self.e_media.get())== False:
            tkMessageBox.showwarning("Pi Presents Editor","Media Directory not found")
            return 0
        return 1

    def apply(self):
        self.save_options()
        self.result=True

    def save_options(self):
        """ save the output of the options edit dialog to file"""
        config=ConfigParser.ConfigParser()
        config.add_section('config')
        config.set('config','home',self.e_home.get())
        config.set('config','media',self.e_media.get())
        with open(self.options_file, 'wb') as optionsfile:
            config.write(optionsfile)
    


# *************************************
# EDIT SHOW AND TRACK CONTENT
# ************************************

class EditItemDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, title, tp, track_types,field_specs,show_refs):
        self.mon=Monitor()
        self.mon.on()
        #save the extra arg to instance variable
        self.tp = tp   # dictionary - the track parameters to be edited
        self.track_types= track_types
        self.field_specs=field_specs
        self.show_refs=show_refs
        if self.show_refs==[]: self.show_refs=['']
        # list of stringvars from which to get edited values
        self.entries=[]

        #and call the base class _init_which calls body immeadiately and apply on OK pressed
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, master):
                    
        # get fields for this type of track               }
        track_fields=self.track_types[self.tp['type']]              
        # populate the dialog box
        row=0
        self.fields=[]
        self.entries=[]
        for field in track_fields:
            values=[]
            if self.field_specs[field]['shape']in("option-menu",'spinbox'):
                if self.field_specs[field]['param']in ('sub-show','start-show'):
                    values=self.show_refs                    
                else:
                    values=self.field_specs[field]['values']
            else:
                values=[]
            obj=self.make_entry(master,self.field_specs[field],row,values)
            if obj<>None: self.fields.append(obj)
            row +=1
        return None # No initial focus


    def buttonbox(self):
        '''add standard button box.
        override to get rid of key bindings which cause trouble with text widget
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
    def make_entry(self,master,field,row,values):
        if field['shape']=="sep":
            Label(master,text='',width=30, anchor=W).grid(row=row,sticky=W)
            return None
        else:
            parameter=field['param']
            if not parameter in self.tp:
                self.mon.log(self,"Value for field not found in opened file: " + parameter)
                return None
            else:
                if field['must']=='yes':
                    bg='pink'
                else:
                    bg='white'
                Label(master,text=field['text'],width=22, anchor=W).grid(row=row,sticky=W)
                if field['shape']=="entry":
                    obj=Entry(master,bg=bg,width=40)
                    obj.insert(END,self.tp[field['param']])
                elif field['shape']=="text":
                    obj=Text(master,bg=bg,width=40,height=4)
                    obj.insert(END,self.tp[field['param']])
                elif field['shape']=='spinbox':
                    obj=Spinbox(master,bg=bg,width=40,values=values,wrap=True)
                    obj.insert(END,self.tp[field['param']])
                elif field['shape']=="browse":
                    obj=Entry(master,bg=bg,width=40)
                    obj.insert(END,self.tp[field['param']])
                elif field['shape']=='option-menu': 
                    self.option_val = StringVar(master)    
                    self.option_val.set(self.tp[field['param']])
                    obj = apply(OptionMenu, [master, self.option_val] + values)
                    self.entries.append(self.option_val)
                    #obj = OptionMenu(master, self.option_val, values)                                   
                obj.grid(row=row,column=1,sticky=W)
                if field['read-only']=='yes':
                    obj.config(state="readonly")
                return obj


    def apply(self):
        track_fields=self.track_types[self.tp['type']]
        row=0
        entry_index=0
        for field in track_fields:
            field_spec=self.field_specs[field]
            if field_spec['shape']<>'sep':
                if field_spec['shape']=='text':
                    self.tp[field_spec['param']]=self.fields[row].get(1.0,END)
                elif field_spec['shape']=='option-menu':
                    self.tp[field_spec['param']]=self.entries[entry_index].get()
                    entry_index+=1
                else:
                    self.tp[field_spec['param']]=self.fields[row].get().strip()
                row +=1
        self.result=True
        return self.result




# ***************************************
# MAIN
# ***************************************


if __name__ == "__main__":
    datestring=" 3 Jan 2013"
    editor = PPEditor()

