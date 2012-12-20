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
    def __init__(self,pp_dir):
        
        StopWatch.global_enable=False
        self.mon=Monitor()
        self.mon.on()
#****************************************
# INTERPRET COMMAND LINE
# ***************************************

        self.options=command_options()
        

        self.show=None
        

        if self.options['debug']==True:
            Monitor.global_enable=True
        else:
            Monitor.global_enable=False
 
        self.mon.log (self, "Pi Presents is starting")
        
        # create  profile  for pp_editor test files if not there.
        
        if not os.path.exists(pp_dir+"/pp_home/pp_profiles/pp_editor"):
            self.mon.log(self,"Making pp_editor directory") 
            os.makedirs(pp_dir+"/pp_home/pp_profiles/pp_editor")
            
            
        #alternative profile path options are used for editor etc.
        if self.options['profile']<>"":
            self.pp_profile_path=self.options['profile']
        else:
            self.pp_profile_path = "/pp_profiles/pp_profile"
        
       #get directory containing the profiles from the command, check if exists, try second and third option
        # allows for a usb stick which is not there, falling back to SDcard and then to an error config.
        home=self.options['usbstick']
        if home <>"":
            # try usb stick for 10 seconds waiting for it to automount
            for i in range (1, 10):
                self.mon.log(self,"Trying USB Stick at: " + home +  " " + str(i))
                if os.path.exists(home + "/pp_home"):
                    self.pp_home= home+"/pp_home"
                    self.mon.log(self,"Using USB Stick at: " + home)
                    break
                time.sleep (1)
        else:
            self.mon.log(self,"USB Stick pp_home not found at " + home +" trying SD Card")
            home=self.options['sdcard']
            if home <>"" and os.path.exists(home+ "/pp_home"):
                self.mon.log(self,"Using SD card at: " + home)
                self.pp_home= home+"/pp_home"
            else:
                self.mon.log(self,"SD card pp_home not found at " + home + "  trying inside pipresents directory")
                #if sys.argv[0].count("/") == 0:
                    #self.pp_home=os.getcwd()+"/pp_home"
                #else:
                    #self.pp_home=os.path.dirname(sys.argv[0])+"/pp_home"
                self.pp_home=pp_dir+"/pp_home"
         

        #and the current profile is in 
        self.pp_profile=self.pp_home+self.pp_profile_path

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
            call(["xset","s", "off"])
            call(["xset","s", "-dpms"])

        # control display of window decorations
        if self.options['fullscreen']==True:
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
        if self.options['fullscreen']==True:
            # allow just 2 pixels for the hidden taskbar at left of screen
            self.window_width=self.screen_width-2
            self.window_height=self.screen_height
            self.root.geometry("%dx%d+0+0" %(self.window_width,self.window_height))
            self.root.attributes('-zoomed','1')
        else:
            self.window_width=self.screen_width-1000
            self.window_height=self.screen_height-100
            self.root.geometry("%dx%d+0+0" %(self.window_width,self.window_height))
        
        #canvas covers the whole window
        self.canvas_height=self.window_height
        self.canvas_width=self.window_width
        
        # make sure focus is set.
        self.root.focus_set()

        #define response to main window closing.
        self.root.protocol ("WM_DELETE_WINDOW", self.on_close_button)

        # Always use CTRL-Break key to close the program as a get out of jail
        self.root.bind("<Break>",self.on_break_key)
        
        #pass all other keys along to 'shows' and hence to 'players'
        self.root.bind("<Escape>", self._escape_pressed)
        self.root.bind("<Up>", self._up_pressed)
        self.root.bind("<Down>", self._down_pressed)
        self.root.bind("<Left>", self._left_pressed)
        self.root.bind("<Right>", self._right_pressed)
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
        self.on_error()
        # !!!!!!!!!!

# *********************
# EXIT APP
# *********************

    def tidy_up(self):
        #turn screen blanking back on
        if self.options['noblank']==True:
            call(["xset","s", "on"])
            call(["xset","s", "+dpms"])
        #terminate any running shows and players     
        if self.show<>None:
            self.show.kill()
        if self.options['gpio']==True:
            self.buttons.kill()
        #close logging files 
        self.mon.finish()

    def on_break_key(self,event):
        self.mon.log(self, "quit received from CTRL-break")
        self.tidy_up()
        exit()
 
    def on_close_button(self):
        self.mon.log(self, "quit received from Close Button")
        self.tidy_up()
        exit()
    
    def on_error(self):
        self.mon.log(self, "exiting because of error")
        self.tidy_up()
        exit()


    def on_shutdown(self):
        if self.buttons.is_pressed(self.Buttons.SHUTDOWN):
            self.tidy_up()
            call(['sudo', 'shutdown', '-h', '-t 5','now'])
            exit()
        else:
            return


# *********************
# Key and button presses
# ********************

    def shutdown_pressed(self):
        self.root.after(5000,self.on_shutdown)

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
    def _left_pressed(self,event): self._key_pressed("left")  
    def _right_pressed(self,event): self._key_pressed("right")  
    def _return_pressed(self,event): self._key_pressed("return")
    def _pause_pressed(self,event): self._key_pressed("p")
        

    def _key_pressed(self,key_name):
        self.mon.log(self, "Key Pressed: "+ key_name)

        #if a show is running pass the key to it.
        if self.show<>None:
            self.show.key_pressed(key_name)
         
            


if __name__ == '__main__':

    # arguement should be the location of pi presents
    pp = PiPresents("/home/pi/pipresents")
    #try:
        #pp = PiPresents()
    #except:
        # traceback.print_exc(file=open("pp_exceptions.log","w"))
        #pass


