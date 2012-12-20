"""
Issue Date 6 Nov 2012
omx-audio, now expects local or hdmi not -o .....
changed OMXPlayer to OMXDriver
bug - pause/resume gets out of sync. kill the instance at end of track with self=None when ending
      - must now create an instance of VideoPlayer for each play of a track
changed pause to a toggle operation
changed test harness into a class.
added button_pressed, possibly key_pressed
key pressed is now passed name of key rather than event.
removed sending other controls to driver from key_pressed
don't need an external stop  function as the escape key does it.
added a ready to play callback
added track level configuration dictionary.
"""

import time

from pp_utils import Monitor
from pp_omxdriver import OMXDriver

from Tkinter import *
import Tkinter as tk

class VideoPlayer:

    _CLOSED = "omx_closed"    #probably will not exist
    _STARTING = "omx_starting"  #track is being prepared
    _PLAYING = "omx_playing"  #track is playing to the screen, may be paused
    _ENDING = "omx_ending"  #track is in the process of ending due to quit or end of track


# ***************************************
# EXTERNAL COMMANDS
# ***************************************

    def __init__(self,
                        canvas, 
                        cd,
                        track_params ):
        """       
            canvas - the canvas onto which the video is to be drawn (not!!)
            cd - configuration dictionary
            track_params - config dictionary for this track overides cd
        """
        self.mon=Monitor()
        self.mon.on()
        
        #instantiate arguments
        self.cd=cd       #configuration dictionary for the videoplayer
        self.canvas = canvas  #canvas onto which video should be played but isn't! Use as widget for alarm
        self.track_params=track_params
        
        # get config from medialist if there.
        if 'omx-audio' in self.track_params and self.track_params['omx-audio']<>"":
            self.omx_audio= self.track_params['omx-audio']
        else:
            self.omx_audio= self.cd['omx-audio']
        if self.omx_audio<>"": self.omx_audio= "-o "+ self.omx_audio
            
        # could put instance generation in play, not sure which is better.
        self.omx=OMXDriver()
        self._tick_timer=None
        self._init_play_state_machine()



    def play(self, track,
                     end_callback,
                     ready_callback,
                     enable_menu=False, 
                     starting_callback=None,
                     playing_callback=None,
                     ending_callback=None):
                         
        #instantiate arguments
        self.ready_callback=ready_callback   #callback when ready to play
        self.end_callback=end_callback         # callback when finished
        self.starting_callback=starting_callback  #callback during starting state
        self.playing_callback=playing_callback    #callback during playing state
        self.ending_callback=ending_callback      # callback dugin ending state
        # enable_menu is not used by videoplayer
 
        # and start playing the video.
        if self.play_state == VideoPlayer._CLOSED:
            self.mon.log(self,">play track received")
            self._start_play_state_machine(track)
            return True
        else:
            self.mon.log(self,"!< play track rejected")
            return False


    def key_pressed(self,key_name):
        if key_name=='':
            return
        elif key_name in ('p',' '):
            self._pause()
            return
        elif key_name=='escape':
            self._stop()
            return



    def button_pressed(self,button,edge):
        if button =='pause':
            self._pause()
            return
        elif button=='stop':
            self._stop()
            return

    def kill(self):
        if self.omx<>None:
            self.omx.kill()
        if self._tick_timer<>None:
            self.canvas.after_cancel(self._tick_timer)
            self._tick_timer=None


# ***************************************
# EXTERNAL COMMANDS
# ***************************************

    def _stop(self):
        # send signal to stop the track to the state machine
        self.mon.log(self,">stop received")
        self._stop_required_signal=True


    #toggles pause
    def _pause(self):
        if self.play_state in (VideoPlayer._PLAYING,VideoPlayer._ENDING):
            self.omx.pause()
            return True
        else:
            self.mon.log(self,"!<pause rejected")
            return False
        

    def _control(self,char):
        if self.play_state==VideoPlayer._PLAYING:
            self.mon.log(self,"> send control ot omx: "+ char)
            self.omx.control(char)
            return True
        else:
            self.mon.log(self,"!<control rejected")
            return False



# ***************************************
# # PLAYING STATE MACHINE
# ***************************************

    """self. play_state controls the playing sequence, it has the following values.
         I am not entirely sure the starting and ending states are required.
         - _closed - the omx process is not running, omx process can be initiated
         - _starting - omx process is running but is not yet able to receive controls
         - _playing - playing a track, controls can be sent
         - _ending - omx is doing its termination, controls cannot be sent
    """

    def _init_play_state_machine(self):
        self._stop_required_signal=False
        self.play_state=VideoPlayer._CLOSED
 
    def _start_play_state_machine(self,track):
        #initialise all the state machine variables
        #self.iteration = 0                             # for debugging
        self._stop_required_signal=False     # signal that user has pressed stop
        self.play_state=VideoPlayer._STARTING
        
        #play the selected track
        options=self.omx_audio+" "+self.cd['omx-other-options']+" "
        self.omx.play(track,options)
        self._tick_timer=self.canvas.after(50, self._play_state_machine)
 

    def _play_state_machine(self):

        
        if self.play_state == VideoPlayer._CLOSED:
            self.mon.log(self,"      State machine: " + self.play_state)
            return 
                
        elif self.play_state == VideoPlayer._STARTING:
            self.mon.log(self,"      State machine: " + self.play_state)
            # if omxplayer is playing the track change to play state
            if self.omx.start_play_signal==True:
                self.mon.log(self,"            <start play signal received from omx")
                self.omx.start_play_signal=False
                # callback to the calling object to e.g remove egg timer.
                if self.ready_callback<>None:
                    self.ready_callback()
                self.play_state=VideoPlayer._PLAYING
                self.mon.log(self,"      State machine: omx_playing started")
            self._do_starting()
            self._tick_timer=self.canvas.after(50, self._play_state_machine)

        elif self.play_state == VideoPlayer._PLAYING:
            # self.mon.log(self,"      State machine: " + self.play_state)
            # service any queued stop signals
            if self._stop_required_signal==True:
                self.mon.log(self,"      Service stop required signal")
                self._stop_omx()
                self._stop_required_signal=False
                self.play_state = VideoPlayer._ENDING
            # omxplayer reports it is terminating so change to ending state
            if self.omx.end_play_signal:                    
                self.mon.log(self,"            <end play signal received")
                self.mon.log(self,"            <end detected at: " + str(self.omx.video_position))
                self.play_state = VideoPlayer._ENDING
            self._do_playing()
            self._tick_timer=self.canvas.after(200, self._play_state_machine)

        elif self.play_state == VideoPlayer._ENDING:
            self.mon.log(self,"      State machine: " + self.play_state)
            self._do_ending()
            # if spawned process has closed can change to closed state
            self.mon.log (self,"      State machine : is omx process running? -  "  + str(self.omx.is_running()))
            if self.omx.is_running() ==False:
                self.mon.log(self,"            <omx process is dead")
                self.play_state = VideoPlayer._CLOSED
                if self.end_callback<>None:
                    self.end_callback("track has terminated")
                self=None
            else:
                self._tick_timer=self.canvas.after(200, self._play_state_machine)


    # allow calling object do things in each state by calling the appropriate callback
 
    def _do_playing(self):
        self.video_position=self.omx.video_position
        self.audio_position=self.omx.audio_position
        if self.playing_callback<>None:
                self.playing_callback() 

    def _do_starting(self):
        self.video_position=0.0
        self.audio_position=0.0
        if self.starting_callback<>None:
                self.starting_callback() 

    def _do_ending(self):
        if self.ending_callback<>None:
                self.ending_callback() 

    def _stop_omx(self):
        # send signal to stop the track to the state machine
        self.mon.log(self,"         >stop omx received from state machine")
        if self.play_state==VideoPlayer._PLAYING:
            self.omx.stop()
            return True
        else:
            self.mon.log(self,"!<stop rejected")
            return False

# *****************
#Test harness follows
# *****************

class Test:
    
    def __init__(self,cd,track,ct):
        
        self.track=track
        self.cd=cd
        self.ct = ct
        self.break_from_loop=False
    
        # create and instance of a Tkinter top level window and refer to it as 'my_window'
        my_window=Tk()
        my_window.title("VideoPlayer Test Harness")
    
        # change the look of the window
        my_window.configure(background='grey')
        window_width=200
        window_height=200
    
        canvas_height=window_height
        canvas_width=window_width
    

        #defne response to main window closing
        my_window.protocol ("WM_DELETE_WINDOW", self.app_exit)
        
        my_window.geometry("%dx%d+200+20" %(window_width,window_height))
    
        my_window.bind("s", self.play_event)
        my_window.bind("p", self.pause_event)
        my_window.bind("q", self.stop_event)
        my_window.bind("l", self.loop_event)
        my_window.bind("n", self.next_event)
        
        #setup a canvas onto which will not be drawn the video!!
        canvas = Canvas(my_window, bg='black')
        canvas.config(height=canvas_height, width=canvas_width)
        canvas.grid(row=1,columnspan=2)
        
        # make sure focus is set on canvas.
        canvas.focus_set()
    
        self.canvas=canvas
        
        self.display_time = tk.StringVar()
        
    # define time/status display for selected track
        time_label = Label(canvas, font=('Comic Sans', 11),
                                fg = 'black', wraplength = 300,
                                textvariable=self.display_time, bg="grey")
        time_label.grid(row=0, column=0, columnspan=1)
    
        my_window.mainloop()
    
    def time_string(self,secs):
        minu = int(secs/60)
        sec = secs-(minu*60)
        return str(minu)+":"+str(int(sec))
    
    #key presses
    
    def play_event(self,event):
        self.vp=VideoPlayer(self.canvas,self.cd,self.ct)
        self.vp.play(self.track,self.on_end,self.do_ready,self.do_starting,self.do_playing,self.do_finishing)
    
    # toggles pause
    def pause_event(self,event):
        self.vp._pause()  #bodge

    def stop_event(self,event):
        self.break_from_loop=True
        self.vp._stop()   #bodge
    
    
    def loop_event(self,event):
      #just kick off the first track, callback decides what to do next
        self.break_from_loop=False
        self.vp=VideoPlayer(self.canvas,self.cd)
        self.vp.play(self.track,self.what_next,self.do_starting,self.do_playing,self.do_finishing)
    
    
    def next_event(self,event):
        self.break_from_loop=False
        self.vp.stop()
    
    
    def what_next(self,message):
        if self.break_from_loop==True:
            self.break_from_loop=False
            print "test harness: loop interupted"
            return
        else:
            self.vp=VideoPlayer(self.canvas,self.cd)
            self.vp.play(self.track,self.what_next,self.do_starting,self.do_playing,self.do_finishing)
    

    
    def on_end(self,message):
        print "Test Class: callback from VideoPlayer says: "+ message
        return
    
    def do_ready(self):
        print "test class message from videoplayer: ready to play"
        return
    
    def do_starting(self):
        print "test class message from videoplayer: do starting"
        return
    
    def do_playing(self):
        self.display_time.set(self.time_string(self.vp.video_position))
        print "test class message from videoplayer: do playing"
        return
    
    def do_finishing(self):
        print "test class messgae from videoplayer: do finishing"
        return
    
    
    def app_exit(self):
        try:
            self.vp
        except AttributeError:
            exit()
        else:
            self.vp.kill()
            return
        # kill the omplayer.bin if it is still running because window has been closed during a track playing.
            exit()

# end of Test Class


if __name__ == '__main__':


    """
    To run the test harness edit track to something suitable then run  with  python pp_videoplayer.py
    
    s - play a track single shot
    p - pause/resume
    q - quit
    
    l - loop the track continuously
    p - as above
    n - skip to next track
    q - stops the track and breaks out of the loop
    """

    #track is used as a global variable in the test  harness.
    track="/home/pi/pipresents/pp_home/media/x t'hresh.mp4"
    #create a dictionary of options and create a videoplayer object
    cd={'omx-other-options' : '-t on',
            'omx-audio' : 'hdmi'}
    Monitor.global_enable=True
    test=Test(cd,track,cd)



                                            




   

