import os
from Tkinter import *
import Tkinter as tk
import PIL.Image
import PIL.ImageTk
import PIL.ImageEnhance

from pp_imageplayer import ImagePlayer
from pp_videoplayer import VideoPlayer
from pp_medialist import MediaList
from pp_utils import Monitor
from pp_messageplayer import MessagePlayer

class MediaShow:

    _CLOSED=0
    _FRONT_PORCH=1
    _PLAYING=2
    _BACK_PORCH=3

# *******************
# External interface
# ********************

    def __init__(self,
                            show,
                            canvas,
                            showlist,
                            pp_home,
                            pp_profile):
        """ canvas - the canvas that the menu is to be written on
            show - the dictionary fo the show to be played
            pp_home - Pi presents data_home directory
            pp_profile - Pi presents profile directory
        """

        self.mon=Monitor()
        self.mon.on()
        
        #instantiate arguments
        self.show =show
        self.showlist=showlist
        self.canvas=canvas
        self.pp_home=pp_home
        self.pp_profile=pp_profile


        # Init variables
        self.player=None
        self.shower=None



    def play(self,end_callback,ready_callback=None, top=False):

        """ displays the mediashow
              end_callback - function to be called when the menu exits
              ready_callback - callback when menu is ready to display (not used)
              top is True when the show is top level (run from [start])
        """

        #instantiate the arguments
        self._end_callback=end_callback
        self._ready_callback=ready_callback
        self.top=top
        self.mon.log(self,"Starting show: " + self.show['show-ref'])

        # check  data files are available.
        self.media_file = self.pp_profile + "/" + self.show['medialist']
        if not os.path.exists(self.media_file):
            self.mon.err(self,"Medialist file not found: "+ self.media_file)
            self._stop("Medialist file not found")

        #create a medialist for the mediashow and read it.
        self.medialist=MediaList()
        self.medialist.open_list(self.media_file)
            
        #init and kick off the mediashow
        self._poll_for_interval_timer=None
        self._poll_for_continue_timer=None
        self._interval_timer=None
        
        self._interval_timer_signal=False
        self._trigger_show_signal=False
        self._restart_show_signal=False
        self._end_mediashow_signal=False
        self._next_track_signal=False
        self._previous_track_signal=False
        self._play_child_signal = False
        
        self._start_front_porch()


   # respond to key presses.
    def key_pressed(self,key_name):
        self.mon.log(self,"received key: " + key_name)
        
        if key_name=='':
            pass
        
        elif key_name=='escape':
            # if next lower show eor player is running pass down to stop the show/track
            # ELSE stop this show except for exceptions
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            elif self.player<>None:
                self.player.key_pressed(key_name)
            else:
            # at top in a manual presentation - restart the presentation
                if self.top == True and self.show['progress']=='manual':
                    self._restart()
                # not at top so stop the show
                elif  self.top == False:
                    self._stop("exit show to higher level")
                else:
                    pass
    
        elif key_name in ('up','down'):
        # if child or sub-show is running and is a show pas to show, track does not use up/down
        # if  otherwise use keys for next or previous
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            else:
                if key_name=='down':
                    self._previous()
                else:
                    self._next()
                
        elif key_name=='return':
            # if child show or sub-show is running and is show - pass down
            # ELSE use Return to start child or to trigger a presentation or exhibit
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            else:
                if self._state==MediaShow._PLAYING  and self.show['has-child']=="yes":
                    self._play_child()
                elif  self._state==MediaShow._FRONT_PORCH and self.show['trigger']in("button","PIR"):
                    self._trigger_show()
                
        elif key_name in ('p',' '):
            # pass down if show or track running.
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            elif self.player<>None:
                self.player.key_pressed(key_name)
 

    def button_pressed(self,button,edge):
        if button=='play': self.key_pressed("return")
        elif  button =='up': self.key_pressed("up")
        elif button=='down': self.key_pressed("down")
        elif button=='stop': self.key_pressed("escape")
        elif button=='pause': self.key_pressed('p')
        elif button=='PIR': self.key_pressed('return')


    def kill(self):
        if self.shower<>None:
            self.mon.log(self,"sent kill to shower")
            self.shower.kill()
        elif self.player<>None:
            self.mon.log(self,"sent kill to player")
            self.player.kill()
        else:
            self._end("killed")


 
    def _tidy_up(self):
        if self._poll_for_continue_timer<>None:
                self.canvas.after_cancel(self._poll_for_continue_timer)
                self._poll_for_continue_timer=None
        if self._poll_for_interval_timer<>None:
                self.canvas.after_cancel(self._poll_for_interval_timer)
                self._poll_for_interval_timer=None
        if self._interval_timer<>None:
            self.canvas.after_cancel(self._interval_timer)
            self._interval_timer=None

# ***************************
# Respond to key/button presses
# ***************************

    def _stop(self,message):
        self._end_mediashow_signal=True
        if self._interval_timer<>None:
            self.canvas.after_cancel(self._interval_timer)


    def _restart(self):
        self._restart_show_signal=True
        if self._interval_timer<>None:
            self.canvas.after_cancel(self._interval_timer)

       
    def _next(self):
        # stop track if running and set signal
        self._next_track_signal=True
        if self.shower<>None:
            self.shower.key_pressed("escape")
        else:
            if self.player<>None:
                self.player.key_pressed("escape")

    def _previous(self):
        self._previous_track_signal=True
        if self.shower<>None:
            self.shower.key_pressed("escape")
        else:
            if self.player<>None:
                self.player.key_pressed("escape")
            
            
    def _play_child(self):
        self._play_child_signal=True
        if self.player<>None:
            self.player.key_pressed("escape")



    def _trigger_show(self):
        self._trigger_show_signal=True
        #message player used internall for ready so kill it.
        self.player.key_pressed("escape")
        
        
# ***************************
# end of show functions
# ***************************

    def _end(self,message):
        self._end_mediashow_signal=False
        self.mon.log(self,"Ending Mediashow: "+ self.show['show-ref'])
        self._tidy_up()
        self._end_callback(message)
        self=None
        return
        
    def _nend(self):
        self._end_mediashow_signal=False
        self.mon.log(self,"Ending Mediashow: "+ self.show['show-ref'])
        self._tidy_up()
        self._end_callback("end from state machine")
        self=None
        return

    def _error(self,message):
        self._end_mediashow_signal=False
        self.mon.log(self,"Ending Mediashow: "+ self.show['show-ref'])
        self._tidy_up()
        self._end_callback(message)
        self=None
        return


# ***************************
# State Machine
# ***************************
 
    def _start_front_porch(self):
        if self.ready_callback<>None:
            self.ready_callback()
        self._state=MediaShow._FRONT_PORCH
        # self.mon.log(self,"Starting front porch with trigger: "+ self.show['trigger'])     
        if self.show['trigger']=="button":
            # blank screen waiting for trigger if auto, otherwise display something
            if self.show['progress']=="manual":
                text="To start the show press 'Play'"
            else:
                text=""

            self.display_message(self.canvas,'text',text,0,self._start_playing)


        elif self.show['trigger']=="PIR":
            # blank screen waiting for trigger
            self.display_message(self.canvas,'text','',0,self._start_playing)      
            
        elif self.show['trigger']=="start":
            self._start_playing()
            
        else:
            self.mon.err(self,"Unknown trigger: "+ self.show['trigger'])
            self._end("Unknown trigger type")
  
        
    def _do_front_porch(self):
        pass
        
    def _start_playing(self):
        self._state=MediaShow._PLAYING
        if self.show['repeat']=="interval" and self.show['repeat-interval']<>0:
            self._interval_timer_signal=False
            self._interval_timer=self.canvas.after(int(self.show['repeat-interval'])*1000,self._end_interval_timer)
        self.medialist.start()
        self._play_selected_track(self.medialist.selected_track())
 
 
    def _do_playing(self):
        # end of a track decide on next thing to do
        # user wants to end 
        if self._end_mediashow_signal==True:
            self._end_mediashow_signal=False
            self._end("show ended by user")
            
        elif self._restart_show_signal==True:
            self._restart_show_signal=False
            self._start_front_porch()
            
        elif self._play_child_signal == True:
            self._play_child_signal=False
            index = self.medialist.index_of_track('pp-child-show')
            if index >=0:
                #don't select the track as need to preserve mediashow sequence.
                child_track=self.medialist.track(index)
                self._display_eggtimer("Loading.....")
                self._play_selected_track(child_track)
            else:
                self.mon.err(self,"Child show not found in medialist: "+ self.show['pp-child-show'])
                self._error("child show not found in medialist")
        
        # skip to next track on user input or display it if manual
        elif self._next_track_signal==True:
            self._next_track_signal=False
            if  self.show['sequence']=="ordered" and self.medialist.at_end()==True:
                self._start_back_porch()
            else:
                self.medialist.next()
                self._play_selected_track(self.medialist.selected_track())
                
        # skip to previous track on user input, or display it if manual
        elif self._previous_track_signal==True:
            self._previous_track_signal=False
            if  self.show['sequence']=="ordered" and self.medialist.at_start()==True:
                self._start_front_porch()
            else:
                self.medialist.previous()
                self._play_selected_track(self.medialist.selected_track())
                
        # progress to next track because previous track is finished and we are on auto        
        elif self.show['progress']=="auto":
                if self.show['sequence']=="ordered" and self.medialist.at_end()==True:
                    self._start_back_porch()
                else:
                    self.medialist.next()
                    self._play_selected_track(self.medialist.selected_track())
                    
        # track has finished by user doing a stop and manual so restart, or naturally but we are on manual so poll for user input                   
        elif self.show['progress']=="manual":
                    self._delete_eggtimer()
                    self._display_eggtimer("Waiting. To show next slide press 'Next'")
                    self._poll_for_continue_timer=self.canvas.after(500,self._do_playing)
                    
        else:
            #unhandled state
            self.mon.err(self,"Unhandled playing event: ")
            self._stop("Unhandled playing event")           


    def _start_back_porch(self):
        self._state=MediaShow._BACK_PORCH
        self.mon.log(self,"Starting back porch with repeat: "+ self.show['repeat'])
        
        #not at top so stop the show to get back to parent
        if self.top==False:
            self._end("Return from Sub Show")
        
        #oneshot - restart the show waiting for trigger. 
        elif self.show['repeat']=="oneshot":
            self._start_front_porch()
            
        #interval - wait for interval timer if interval is non-zero
        elif self.show['repeat']=="interval":
            if int(self.show['repeat-interval'])==0:
                self._start_front_porch()
            else:
                self._poll_for_interval_timer=self.canvas.after(1000,self._do_back_porch)
                
        else:
            self.mon.err(self,"Unknown repeat type: "+ self.show['repeat'])
            self._end("Unknown repeat type")


    def _do_back_porch(self):
        # wait for interval timer then restart show
        if self._interval_timer_signal==True:
            self._interval_timer_signal=False
            self._start_front_porch()
        else:
            self._poll_for_interval_timer=self.canvas.after(1000,self._do_back_porch)


    def _end_interval_timer(self):
        self._interval_timer_signal=True
 

        

# ***************************
# Dispatching to Players/Shows 
# ***************************

    # used to display internal messages in situations where a medialist entry could be used.
    def display_message(self,canvas,source,content,duration,_display_message_callback):
            self._display_message_callback=_display_message_callback
            tp={'duration':duration,'message-colour':'white','message-font':'Helvetica 20 bold'}
            self.player=MessagePlayer(canvas,tp,tp)
            self.player.play(content,self._display_message_end,None)

    def   _display_message_end(self,message):
        self.player=None
        if message=="killed":
            self._end(message)
        else:
            self._display_message_callback()


    def complete_path(self,selected_track):
        #  complete path of the filename of the selected entry
        track_file = selected_track['location']
        if track_file[0]=="+":
                track_file=self.pp_home+track_file[1:]
        self.mon.log(self,"Track to play is: "+ track_file)
        return track_file     
         
        if os.path.exists(track_file)==False:
            self.mon.err(self,"Track not found: "+ track_file)
            self._error("track file not found")
            return False



    def _play_selected_track(self,selected_track):
        """ selects the appropriate player from type field of the medialist and computes
              the parameters for that type
              selected track is a dictionary for the track/show
        """
        self.canvas.delete(ALL)
        if self.show['progress']=="manual":
            self._display_eggtimer("Loading.....")

        # is menu required
        if self.show['has-child']=="yes":
            enable_child=True
        else:
            enable_child=False

        #dispatch track by type
        self.player=None
        self.shower=None
        track_type = selected_track['type']
        self.mon.log(self,"Track type is: "+ track_type)
        
        if track_type=="video":
            # create a videoplayer
            track_file=self.complete_path(selected_track)
            self.player=VideoPlayer(self.canvas,self.show,selected_track)
            self.player.play(track_file,
                                        self.end_player,
                                        self.ready_callback,
                                        enable_menu=enable_child)
                                        
        elif track_type=="image":
            track_file=self.complete_path(selected_track)
            # images played from menus don't have children
            self.player=ImagePlayer(self.canvas,self.show,selected_track)
            self.player.play(track_file,
                                    self.end_player,
                                    self.ready_callback,
                                    enable_menu=enable_child)
                                    
        elif track_type=="message":
            # bit odd because MessagePlayer is used internally to display text. 
            text=selected_track['text']
            self.player=MessagePlayer(self.canvas,self.show,selected_track)
            self.player.play(text,
                                    self.end_player,
                                    self.ready_callback,
                                    enable_menu=enable_child
                                    )
         
 
        elif track_type=="show":
            # get the show from the showlist
            index = self.showlist.index_of_show(selected_track['sub-show'])
            if index >=0:
                self.showlist.select(index)
                selected_show=self.showlist.selected_show()
            else:
                self.mon.err(self,"Show not found in showlist: "+ selected_track['sub-show'])
                self._stop("Unknown show")
                
            if selected_show['type']=="mediashow":    
                self.shower= MediaShow(selected_show,
                                                                self.canvas,
                                                                self.showlist,
                                                                self.pp_home,
                                                                self.pp_profile)
                self.shower.play(self.end_shower,top=False)

            
            elif selected_show['type']=="menu":
                self.shower= MenuShow(selected_show,
                                                        self.canvas,
                                                        self.showlist,
                                                        self.pp_home,
                                                        self.pp_profile)
                self.shower.play(self.end_shower,top=False)
                
            else:
                self.mon.err(self,"Unknown Show Type: "+ selected_show['type'])
                self._stop("Unknown show type")  
            
        else:
            self.mon.err(self,"Unknown Track Type: "+ track_type)
            self._stop("Unknown track type")            


    def ready_callback(self):
        self._delete_eggtimer()
        
        
    def end_player(self,message):
        self.mon.log(self,"Returned from player with message: "+ message)
        self.player=None
        if message=="killed":
            self._end(message)
        elif self.show['progress']=="manual":
            self._display_eggtimer("Stopping..")
        self._do_playing()

    def end_shower(self,message):
        self.mon.log(self,"Returned from shower with message: "+ message)
        self.shower=None
        if message=="killed":
            self._end(message)
        elif self.show['progress']=="manual":
            self._display_eggtimer("Stopping..")
        self._do_playing()  
        
        
    def _display_eggtimer(self,text):
        self.canvas.create_text(int(self.canvas['width'])/2,
                                              int(self.canvas['height'])/2,
                                                  text= text,
                                                  fill='white',
                                                  font="Helvetica 20 bold")
        self.canvas.update_idletasks( )


    def _delete_eggtimer(self):
            self.canvas.delete(ALL)
        
from pp_menushow import MenuShow
