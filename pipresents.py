#! /usr/bin/env python

"""
Part of Pi Presents
Pi presents is a presentation package, running on the Raspberry Pi, for museum exhibits, galleries, and presentations.
Copyright 2012, Ken Thompson
Licence:

See manual.txt for instructions.
"""
import os
import sys
import traceback
from subprocess import call
import time

from Tkinter import *
import Tkinter as tk

from pp_options import command_options
from pp_showlist import ShowList
from pp_menushow import MenuShow
from pp_mediashow import MediaShow
from pp_utils import Monitor
from pp_utils import StopWatch


class PiPresents:
    def __init__(self):
        
        StopWatch.global_enable=False

#****************************************
# INTERPRET COMMAND LINE
# ***************************************

        self.options=command_options()
        
        # where am I?
        if self.options['code']=="":
            pp_dir="/home/pi/pipresents"
        else:
            pp_dir=self.options['code']
            
        if not os.path.exists(pp_dir+"/pipresents.py"):
            tkMessageBox.showwarning("Pi Presents","Bad Application Directory")
            exit()
            
        #Initialise logging
        Monitor.log_path=pp_dir
        self.mon=Monitor()
        self.mon.on()
        if self.options['debug']==True:
            Monitor.global_enable=True
        else:
            Monitor.global_enable=False
 
        self.mon.log (self, "Pi Presents is starting")
        
        #self.show=None
        
        # create  profile  for pp_editor test files if already not there.
        if not os.path.exists(pp_dir+"/pp_home/pp_profiles/pp_editor"):
            self.mon.log(self,"Making pp_editor directory") 
            os.makedirs(pp_dir+"/pp_home/pp_profiles/pp_editor")
            
            
        #profile path from -p option
        if self.options['profile']<>"":
            self.pp_profile_path="/pp_profiles/"+self.options['profile']
        else:
            self.pp_profile_path = "/pp_profiles/pp_profile"
        
       #get directory containing pp_home from the command,
        if self.options['home'] =="":
            home = "/home/pi/pp_home"
        else:
            home = self.options['home'] + "/pp_home"
                   
        #check if pp_home exists
        #  falling back to an error config.
        # try for 10 seconds to allow usb stick to automount
        self.pp_home=pp_dir+"/pp_home"
        for i in range (1, 10):
            self.mon.log(self,"Trying pp_home at: " + home +  " " + str(i))
            if os.path.exists(home):
                self.mon.log(self,"Using pp_home at: " + home)
                self.pp_home=home
                break
            time.sleep (1)

        #check profile exists, if not default to error profile inside pipresents
        self.pp_profile=self.pp_home+self.pp_profile_path
        if not os.path.exists(self.pp_profile):
            self.pp_profile=pp_dir+"/pp_home/pp_profiles/pp_profile"
            
        #initialise the showlists and read the showlists
        self.showlist=ShowList()
        self.showlist_file= self.pp_profile+ "/pp_showlist.json"
        if os.path.exists(self.showlist_file):
            self.showlist.open_json(self.showlist_file)
        else:
            self.mon.err(self,"showlist not found at "+self.showlist_file)
            self.on_error()
 
        # get the starter show from the showlist
        index = self.showlist.index_of_show('start')
        if index >=0:
            self.showlist.select(index)
            self.starter_show=self.showlist.selected_show()
        else:
            self.mon.err(self,"Show [start] not found in showlist")
            self.on_error()
            
# ********************
# SET UP THE GUI
# ********************

        #turn off the screenblanking and saver
        if self.options['noblank']==True:
            print "blank off"
            call(["xset","s", "off"])
            call(["xset","s", "-dpms"])

        # control display of window decorations
        if self.options['fullscreen']<>"partial":
            self.root = Tk(className="fspipresents")
        else:
              self.root = Tk(className="pipresents")          

        self.title='Pi Presents - '+ self.pp_profile
        self.icon_text= 'Pi Presents'
        
        self.root.title(self.title)
        self.root.iconname(self.icon_text)
        
        # get size of the screen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # set window dimensions
        self.window_height=self.screen_height
        self.window_width=self.screen_width
        self.window_x=0
        self.window_y=0
        if self.options['fullscreen']<>"partial":
            bar=self.options['fullscreen']
            # allow just 2 pixels for the hidden taskbar
            if bar in ('left','right'):
                self.window_width=self.screen_width-2
            else:
                self.window_height=self.screen_height-2
            if bar =="left":
                self.window_x=2
            if bar =="top":
                self.window_y=2   
            self.root.geometry("%dx%d%+d%+d"  % (self.window_width,self.window_height,self.window_x,self.window_y))
            self.root.attributes('-zoomed','1')
        else:
            self.window_width=self.screen_width-200
            self.window_height=self.screen_height-200
            self.window_x=50
            self.root.geometry("%dx%d%+d%+d" % (self.window_width,self.window_height,self.window_x,self.window_y))

        
        #canvas covers the whole window
        self.canvas_height=self.window_height
        self.canvas_width=self.window_width
        
        # make sure focus is set.
        self.root.focus_set()

        #define response to main window closing.
        self.root.protocol ("WM_DELETE_WINDOW", self.on_break_key)

        # Always use CTRL-Break key to close the program as a get out of jail
        self.root.bind("<Break>",self.e_on_break_key)
        
        #pass all other keys along to 'shows' and hence to 'players'
        self.root.bind("<Escape>", self._escape_pressed)
        self.root.bind("<Up>", self._up_pressed)
        self.root.bind("<Down>", self._down_pressed)
        self.root.bind("<Return>", self._return_pressed)
        self.root.bind("<space>", self._pause_pressed)
        self.root.bind("p", self._pause_pressed)

        #setup a canvas onto which will be drawn the images or text
        self.canvas = Canvas(self.root, bg='black')
        self.canvas.config(height=self.canvas_height, width=self.canvas_width)
        self.canvas.grid(row=1,columnspan=2)
        
        # make sure focus is set on canvas.
        self.canvas.focus_set()


# ****************************************
# INITIALISE THE APPLICATION AND START
# ****************************************
        self.shutdown_required=False
        
        #kick off GPIO if enabled by command line option
        if self.options['gpio']==True:
            from pp_buttons import Buttons
            # initialise the buttons connected to GPIO
            self.Buttons=Buttons
            self.buttons = Buttons(self.root,20,self.button_pressed)
            self.buttons.poll()

            
        #  kick off the initial show            
        self.show=None
        # get the start show from the showlist
        index = self.showlist.index_of_show(self.starter_show['start-show'])
        if index >=0:
            self.showlist.select(index)
            self.start_show=self.showlist.selected_show()
        else:
            self.mon.err(self,"Show not found in showlist: "+ self.starter_show['start-show'])
            self.on_error()
            
        if self.start_show['type']=="mediashow":
            self.show= MediaShow(self.start_show,
                                                            self.canvas,
                                                            self.showlist,
                                                            self.pp_home,
                                                            self.pp_profile)
            self.show.play(self._on_show_end,top=True)
            self.root.mainloop( )     
            
        elif self.start_show['type']=="menu":
            self.show= MenuShow(self.start_show,
                                                    self.canvas,
                                                    self.showlist,
                                                    self.pp_home,
                                                    self.pp_profile)
            self.show.play(self._on_show_end,top=True)
            self.root.mainloop( )     
            
        else:
            self.mon.err(self,"unknown mediashow type in start show - "+ self.start_show['type'])
            self.on_error()
    
     
    def _on_show_end(self,message):
        self.mon.log(self,"Show ended with message: " + message)
        self.show=None
        if message=="killed":
            self.mon.log(self,"kill received - exiting")
            self.on_kill_callback()
        else:
            # should never be here
            self.on_error()


# *********************
# EXIT APP
# *********************

    def tidy_up(self):
        #turn screen blanking back on
        if self.options['noblank']==True:
            call(["xset","s", "on"])
            call(["xset","s", "+dpms"])
        if self.options['gpio']==True:
            self.buttons.kill()
        #close logging files 
        self.mon.finish()

    def on_kill_callback(self):
        self.tidy_up()
        if self.shutdown_required==True:
            call(['sudo', 'shutdown', '-h', '-t 5','now'])
        else:
            exit()

 
    def on_error(self):
        self.mon.log(self, "exiting because of error")
        self.tidy_up()
        exit()



# *********************
# Key and button presses
# ********************

    def shutdown_pressed(self):
        self.root.after(5000,self.on_shutdown_delay)

    def on_shutdown_delay(self):
        if self.buttons.is_pressed(self.Buttons.SHUTDOWN):
            self.shutdown_required=True
            self.on_break_key()

    def button_pressed(self,index,button,edge):
        self.mon.log(self, "Button Pressed: "+button)
        if button=="shutdown":
            self.shutdown_pressed()
        else:
            if self.show<>None:
                self.show.button_pressed(button,edge)
  
    # key presses
    def _escape_pressed(self,event): self._key_pressed("escape")              
    def _up_pressed(self,event): self._key_pressed("up")  
    def _down_pressed(self,event): self._key_pressed("down")  
    def _return_pressed(self,event): self._key_pressed("return")
    def _pause_pressed(self,event): self._key_pressed("p")
        

    def _key_pressed(self,key_name):
        self.mon.log(self, "Key Pressed: "+ key_name)
        # if a show is running pass the key to it.
        if self.show<>None:
            self.show.key_pressed(key_name)
         
    def on_break_key(self):
        self.mon.log(self, "kill received from user")
        #terminate any running shows and players     
        if self.show<>None:
            self.mon.log(self,"kill sent to show")   
            self.show.kill()
    
    def e_on_break_key(self,event):
        self.on_break_key()

if __name__ == '__main__':

    pp = PiPresents()
    #try:
        #pp = PiPresents()
    #except:
        # traceback.print_exc(file=open("/home/pi/pp_exceptions.log","w"))
        #pass


