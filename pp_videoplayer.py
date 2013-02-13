
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
        self.error=False
        self.terminate_required=False
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
        self.ending_callback=ending_callback      # callback during ending state
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


    def terminate(self,reason):
        # circumvents state machine
        self.terminate_required=True
        if self.omx<>None:
            self.mon.log(self,"sent terminate to omxdriver")
            self.omx.terminate(reason)
        else:
            self.mon.log(self,"terminate, omxdriver not running")
            self._end()
            
                

        
# ***************************************
# INTERNAL FUNCTIONS
# ***************************************

    # respond to normal stop
    def _stop(self):
        # send signal to stop the track to the state machine
        self.mon.log(self,">stop received")
        self._stop_required_signal=True

    #respond to internal error
    def _error(self):
        self.error=True
        self._stop_required_signal=True

    #toggle pause
    def _pause(self):
        if self.play_state in (VideoPlayer._PLAYING,VideoPlayer._ENDING):
            self.omx.pause()
            return True
        else:
            self.mon.log(self,"!<pause rejected")
            return False
        
    # other control when playing, used?
    def _control(self,char):
        if self.play_state==VideoPlayer._PLAYING:
            self.mon.log(self,"> send control ot omx: "+ char)
            self.omx.control(char)
            return True
        else:
            self.mon.log(self,"!<control rejected")
            return False

    # called to end omxdriver
    def _end(self):
            if self._tick_timer<>None:
                self.canvas.after_cancel(self._tick_timer)
                self._tick_timer=None
            if self.error==True:
                self.end_callback("error",'error')
                self=None 
            elif self.terminate_required==True:
                self.end_callback("killed",'killed')
                self=None
            else:
                self.end_callback('normal',"track has terminated")
                self=None

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
        # and start polling for state changes
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
                self._end()
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

            
