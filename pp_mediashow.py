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
from pp_resourcereader import ResourceReader

class MediaShow:


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

        # open resources
        self.rr=ResourceReader()

        # Init variables
        self.player=None
        self.shower=None
        self._poll_for_interval_timer=None
        self._poll_for_continue_timer=None
        self._waiting_for_interval=False
        self._interval_timer=None
        self.error=False
        
        self._interval_timer_signal=False
        self._end_mediashow_signal=False
        self._next_track_signal=False
        self._previous_track_signal=False
        self._play_child_signal = False
        self._req_next='nil'

        self._state='closed'


    def play(self,end_callback,ready_callback=None, top=False,command='nil'):

        """ displays the mediashow
              end_callback - function to be called when the menu exits
              ready_callback - callback when menu is ready to display (not used)
              top is True when the show is top level (run from [start])
        """

        #instantiate the arguments
        self._end_callback=end_callback
        self._ready_callback=ready_callback
        self.top=top
        self.command=command
        self.mon.log(self,"Starting show: " + self.show['show-ref'])

        # check  data files are available.
        self.media_file = self.pp_profile + "/" + self.show['medialist']
        if not os.path.exists(self.media_file):
            self.mon.err(self,"Medialist file not found: "+ self.media_file)
            self._end('error',"Medialist file not found")


        #create a medialist for the mediashow and read it.
        self.medialist=MediaList()
        if self.medialist.open_list(self.media_file,self.showlist.sissue())==False:
            self.mon.err(self,"Version of medialist different to Pi Presents")
            self._end('error',"Version of medialist different to Pi Presents")

        self._wait_for_trigger()


   # respond to key presses.
    def key_pressed(self,key_name):
        self.mon.log(self,"received key: " + key_name)
        
        if key_name=='':
            pass
        
        elif key_name=='escape':
            # if next lower show is running pass down to stop the show and lower level
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            # if not at top stop the show
            else:
                if self.top == False:
                    self._end_mediashow_signal=True
                    # and if a track is running stop that first
                    if self.player<>None:
                        self.player.key_pressed(key_name)
                else:
                    # at top level in a manual presentation stop the track
                    if self.show['progress']=='manual':
                        if self.player<>None:
                            self.player.key_pressed(key_name)
    
        elif key_name in ('up','down'):
        # if child or sub-show is running and is a show pass to show, track does not use up/down
        # otherwise use keys for next or previous
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            else:
                if key_name=='up':
                    self._previous()
                else:
                    self._next()
                
        elif key_name=='return':
            # if child show or sub-show is running and is show - pass down- player does not use return
            # ELSE use Return to start child or to start the show if waiting
            if self.shower<>None:
                self.shower.key_pressed(key_name)
            else:
                if self._state=='playing':
                    if self.show['has-child']=='yes':
                        self._play_child_signal=True
                        # and stop the current track if its running
                        if self.player<>None:
                            self.player.key_pressed("escape")
                else:
                    self._start_show()

        elif key_name=='pir':
                self._start_show()
                
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
        elif button=='PIR': self.key_pressed('pir')


    # kill or error
    def terminate(self,reason):
        if self.shower<>None:
            self.mon.log(self,"sent terminate to shower")
            self.shower.terminate(reason)
        elif self.player<>None:
            self.mon.log(self,"sent terminate to player")
            self.player.terminate(reason)
        else:
            self._end(reason,'terminated without terminating shower or player')

 
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

    def resource(self,section,item):
        value=self.rr.get(section,item)
        if value==False:
            self.mon.err(self, "resource: "+section +': '+ item + " not found" )
            self.terminate("error")
        else:
            return value

# ***************************
# Respond to key/button presses
# ***************************

    def _stop(self,message):
        self._end_mediashow_signal=True
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
     
        
# ***************************
# end of show functions
# ***************************

    def _end(self,reason,message):
        self._end_mediashow_signal=False
        self.mon.log(self,"Ending Mediashow: "+ self.show['show-ref'])
        self._tidy_up()
        self._end_callback(reason,message)
        self=None
        return
        



# ***************************
# Show sequencer
# ***************************
 
    def _wait_for_trigger(self):
        self._state='waiting'
        if self.ready_callback<>None:
            self.ready_callback()

        self.mon.log(self,"Waiting for trigger: "+ self.show['trigger'])
        
        if self.show['trigger']=="button":
            # blank screen waiting for trigger if auto, otherwise display something
            if self.show['progress']=="manual":
                text= self.resource('mediashow','m01')
            else:
                text=""
            self.display_message(self.canvas,'text',text,0,self._start_show)


        elif self.show['trigger']=="PIR":
            # blank screen waiting for trigger
            text = self.resource('mediashow','m02')
            self.display_message(self.canvas,'text',text,0,self._start_show)      
            
        elif self.show['trigger']=="start":
            self._start_show()
            
        else:
            self.mon.err(self,"Unknown trigger: "+ self.show['trigger'])
            self._end('error',"Unknown trigger type")
  
        

    def _start_show(self):
        self._state='playing'
        self._direction='forward'
        # start interval timer
        if self.show['repeat']=="interval" and self.show['repeat-interval']<>0:
            self._interval_timer_signal=False
            self._interval_timer=self.canvas.after(int(self.show['repeat-interval'])*1000,self._end_interval_timer)
        # and play the first track unless commanded otherwise
        if self.command=='backward':
            self.medialist.finish()
        else:
            self.medialist.start()
        self._play_selected_track(self.medialist.selected_track())
 
 
    def _what_next(self):
        self._direction='forward'
        
        # user wants to end, wait for any shows or tracks to have ended then end show
        if self._end_mediashow_signal==True:
            if self.player==None and self.shower==None:
                self._end_mediashow_signal=False
                self._end('normal',"show ended by user")
            else:
                pass
            
        #returning from a subshow needing to move onward 
        elif self._req_next=='do-next':
            self._req_next='nil'
            self.medialist.next()
            self._play_selected_track(self.medialist.selected_track())
            
        #returning from a subshow needing to move backward 
        elif self._req_next=='do-previous':
            self._req_next='nil'
            self._direction='backward'
            self.medialist.previous()
            self._play_selected_track(self.medialist.selected_track())         
               
        # user wants to play child
        elif self._play_child_signal == True:
            self._play_child_signal=False
            index = self.medialist.index_of_track('pp-child-show')
            if index >=0:
                #don't select the track as need to preserve mediashow sequence.
                child_track=self.medialist.track(index)
                self._display_eggtimer(self.resource('mediashow','m07'))
                self._play_selected_track(child_track)
            else:
                self.mon.err(self,"Child show not found in medialist: "+ self.show['pp-child-show'])
                self._end('error',"child show not found in medialist")
        
        # skip to next track on user input
        elif self._next_track_signal==True:
            self._next_track_signal=False
            if self.medialist.at_end()==True:
                if  self.show['sequence']=="ordered" and self.show['repeat']=='oneshot' and self.top==False:
                    self._end('do-next',"Return from Sub Show")
                else:
                    self.medialist.next()
                    self._play_selected_track(self.medialist.selected_track())               
            else:
                self.medialist.next()
                self._play_selected_track(self.medialist.selected_track())
                
        # skip to previous track on user input
        elif self._previous_track_signal==True:
            self._previous_track_signal=False
            self._direction='backward'
            if self.medialist.at_start()==True:
                if  self.show['sequence']=="ordered" and self.show['repeat']=='oneshot' and self.top==False:
                    self._end('do-previous',"Return from Sub Show")
                else:
                    self.medialist.previous()
                    self._play_selected_track(self.medialist.selected_track())               
            else:
                self.medialist.previous()              
                self._play_selected_track(self.medialist.selected_track())
        

        # track is finished and we are on auto        
        elif self.show['progress']=="auto":
            if self.medialist.at_end()==True:
                if self.show['sequence']=="ordered" and self.show['repeat']=='oneshot' and self.top==False:
                    self._end('do-next',"Return from Sub Show")
                    
                #### elif    
                elif self.show['sequence']=="ordered" and self.show['repeat']=='oneshot' and self.top==True:
                    self._wait_for_trigger()

                elif self._waiting_for_interval==True:
                    if self._interval_timer_signal==True:
                        self._interval_timer_signal=False
                        self._waiting_for_interval=False
                        self._start_show()
                    else:
                        self._poll_for_interval_timer=self.canvas.after(1000,self._what_next)
 
                elif self.show['sequence']=="ordered" and self.show['repeat']=='interval' and int(self.show['repeat-interval'])>0:
                    self._waiting_for_interval=True
                    self._poll_for_interval_timer=self.canvas.after(1000,self._what_next) 
                    
                elif self.show['sequence']=="ordered" and self.show['repeat']=='interval' and int(self.show['repeat-interval'])==0:
                    self.medialist.next()
                    self._play_selected_track(self.medialist.selected_track())
                           
                else:
                    self.mon.err(self,"Unhandled playing event: ")
                    self._end('error',"Unhandled playing event")
                    
            else:
                self.medialist.next()
                self._play_selected_track(self.medialist.selected_track())
                    
        # track has finished and we are on manual progress               
        elif self.show['progress']=="manual":
                    self._delete_eggtimer()
                    self._display_eggtimer(self.resource('mediashow','m03'))
                    self._poll_for_continue_timer=self.canvas.after(500,self._what_next)
                    
        else:
            #unhandled state
            self.mon.err(self,"Unhandled playing event: ")
            self._end('error',"Unhandled playing event")           



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

    def   _display_message_end(self,reason,message):
        self.player=None
        if reason in ('error','killed'):
            self._end(reason,message)
        else:
            self._display_message_callback()


    def complete_path(self,selected_track):
        #  complete path of the filename of the selected entry
        track_file = selected_track['location']
        if track_file[0]=="+":
                track_file=self.pp_home+track_file[1:]
        self.mon.log(self,"Track to play is: "+ track_file)
        return track_file     
         
        


    def _play_selected_track(self,selected_track):
        """ selects the appropriate player from type field of the medialist and computes
              the parameters for that type
              selected track is a dictionary for the track/show
        """
        self.canvas.delete(ALL)
        if self.show['progress']=="manual":
            self._display_eggtimer(self.resource('mediashow','m04'))

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
                self._end('error',"Unknown show")
                
            if selected_show['type']=="mediashow":    
                self.shower= MediaShow(selected_show,
                                                                self.canvas,
                                                                self.showlist,
                                                                self.pp_home,
                                                                self.pp_profile)
                self.shower.play(self.end_shower,top=False,command=self._direction)

            elif selected_show['type']=="liveshow":    
                self.shower= LiveShow(selected_show,
                                                                self.canvas,
                                                                self.showlist,
                                                                self.pp_home,
                                                                self.pp_profile)
                self.shower.play(self.end_shower,top=False,command='nil')
            
            elif selected_show['type']=="menu":
                self.shower= MenuShow(selected_show,
                                                        self.canvas,
                                                        self.showlist,
                                                        self.pp_home,
                                                        self.pp_profile)
                self.shower.play(self.end_shower,top=False,command='nil')
                
            else:
                self.mon.err(self,"Unknown Show Type: "+ selected_show['type'])
                self._end('error'"Unknown show type")  
            
        else:
            self.mon.err(self,"Unknown Track Type: "+ track_type)
            self._end('error',"Unknown track type")            


    def ready_callback(self):
        self._delete_eggtimer()
        
        
    def end_player(self,reason,message):
        self._req_next='nil'
        self.mon.log(self,"Returned from player with message: "+ message)
        self.player=None
        if reason in("killed","error"):
            self._end(reason,message)
        elif self.show['progress']=="manual":
            self._display_eggtimer(self.resource('mediashow','m05'))
            self._req_next=reason
            self._what_next()
        else:
            self._req_next=reason
            self._what_next()

    def end_shower(self,reason,message):
        self._req_next='nil'
        self.mon.log(self,"Returned from shower with message: "+ message)
        self.shower=None
        if reason in("killed","error"):
            self._end(reason,message)
        elif self.show['progress']=="manual":
            self._display_eggtimer(self.resource('mediashow','m06'))
            self._req_next=reason
            self._what_next() 
        else:
            self._req_next=reason
            self._what_next() 
        
        
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
from pp_liveshow import LiveShow
