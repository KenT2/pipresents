"""
Issue Date 6 Nov 2012

To run the test harness edit track to something suitable then run  with  python pp_videoplayer.py

s - play a track single shot
p - pause
r - resume
q - quit

l - loop the track continuously
p,r as above
n - skip to next track
q - stops the track and breaks out of the loop

still not 100% bomb proof, if n is pressed too fast p and r get reversed.
Think I might need to create an instance of OMXPlayer for each track so state is guaranteed to get initilaised

enjoy!
"""

import time

from pp_utils import Monitor
from pp_omxplayer import OMXPlayer

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

    def __init__(self,canvas, cd ):

        self.mon=Monitor()
        self.mon.off()
        
        self.cd=cd       #configuration dictionary for the videoplayer
        self.canvas = canvas  #canvas onto which video should be played but isn't! Use as widget for alarm

        # could put instance generation in play, not sure which is better.
        self.omx=OMXPlayer()
        self._init_play_state_machine()



    def play(self, track, finished_callback=None,
                     starting_callback=None,
                     playing_callback=None,
                     ending_callback=None):
        self.mon.log(">play track received")
        if self.play_state==VideoPlayer._CLOSED:
            self.finished_callback=finished_callback
            self.starting_callback=starting_callback
            self.playing_callback=playing_callback
            self.ending_callback=ending_callback
            self._start_play_state_machine(track)
            return True
        else:
            self.mon.log("!< play track rejected")
            return False

    def stop(self):
        # send signal to stop the track to the state machine
        self.mon.log(">stop received")
        self._stop_required_signal=True


    def kill(self):
        try:
            self.omx
        except AttributeError:
            return
        else:
            self.omx.kill()
            return

    def pause(self):
        if self.play_state==VideoPlayer._PLAYING:
            self.omx.pause()
            return True
        else:
            self.mon.log("!<pause rejected")
            return False
        
    def resume(self):
        if self.play_state==VideoPlayer._PLAYING:
            self.omx.resume()
            return True
        else:
            self.mon.log("!<resume rejected")
            return False


    def control(self,char):
        if self.play_state==VideoPlayer._PLAYING:
            self.omx.control(char)
            return True
        else:
            self.mon.log("!<control rejected")
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
        options=" "+ self.cd['omx-audio']+" "+self.cd['omx-other-options']+" "
        self.omx.play(track,options)
        self.canvas.after(50, self._play_state_machine)
 

    def _play_state_machine(self):
        # self.mon.log ("******Iteration: " + str(self.iteration))
        #self.iteration +=1
        
        if self.play_state == VideoPlayer._CLOSED:
            self.mon.log("      State machine: " + self.play_state)
            return 
                
        elif self.play_state == VideoPlayer._STARTING:
            self.mon.log("      State machine: " + self.play_state)
            # if omxplayer is playing the track change to play state
            if self.omx.start_play_signal==True:
                self.mon.log("            <start play signal received from omx")
                self.omx.start_play_signal=False
                self.play_state=VideoPlayer._PLAYING
                self.mon.log("      State machine: omx_playing started")
            self._do_starting()
            self.canvas.after(50, self._play_state_machine)

        elif self.play_state == VideoPlayer._PLAYING:
            # self.mon.log("      State machine: " + self.play_state)
            # service any queued stop signals
            if self._stop_required_signal==True:
                self.mon.log("      Service stop required signal")
                self._stop_omx()
                self._stop_required_signal=False
                self.play_state = VideoPlayer._ENDING
            # omxplayer reports it is terminating so change to ending state
            if self.omx.end_play_signal:                    
                self.mon.log("            <end play signal received")
                self.mon.log("            <end detected at: " + str(self.omx.video_position))
                self.play_state = VideoPlayer._ENDING
            self._do_playing()
            self.canvas.after(200, self._play_state_machine)

        elif self.play_state == VideoPlayer._ENDING:
            self.mon.log("      State machine: " + self.play_state)
            self._do_ending()
            # if spawned process has closed can change to closed state
            self.mon.log ("      State machine : is omx process running? -  "  + str(self.omx.is_running()))
            if self.omx.is_running() ==False:
                self.mon.log("            <omx process is dead")
                self.play_state = VideoPlayer._CLOSED
                if self.finished_callback<>None:
                    self.finished_callback("track has terminated")
            self.canvas.after(200, self._play_state_machine)


    # do things in each state by calling the appropriate callback
 
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
        self.mon.log("         >stop omx received from state machine")
        if self.play_state==VideoPlayer._PLAYING:
            self.omx.stop()
            return True
        else:
            self.mon.log("!<stop rejected")
            return False

# *****************
#Test harness follows
# *****************

def time_string(secs):
    minu = int(secs/60)
    sec = secs-(minu*60)
    return str(minu)+":"+str(int(sec))

#key presses

def play_event(event):
    vp.play(track,on_end,do_starting,do_playing,do_finishing)
    
def pause_event(event):
    vp.pause()

def resume_event(event):
    vp.resume()

def stop_event(event):
    global break_from_loop
    break_from_loop=True
    vp.stop()


def loop_event(event):
  #just kick off the first track, callback decides what to do next
    global break_from_loop
    break_from_loop=False
    vp.play(track,what_next,do_starting,do_playing,do_finishing)


def next_event(event):
    break_from_loop=False
    vp.stop()


def what_next(message):
    global break_from_loop
    if break_from_loop==True:
        break_from_loop=False
        print "test harness: loop interupted"
        return
    else:
        vp.play(track,what_next,do_starting,do_playing,do_finishing)



def on_end(message):
    #print "Test harness: callback from VideoPlayer says: "+ message
    return

def do_starting():
    #print "test harness: do starting"
    return

def do_playing():
    display_time.set(time_string(vp.video_position))
    return

def do_finishing():
    # print "test harness: do finishing"
    return


def app_exit():
    # kill the ompllayer.bin if it is still running because window has been closed during a track playing.
        vp.kill()
        exit()



if __name__ == '__main__':

    global break_from_loop
     
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
    my_window.protocol ("WM_DELETE_WINDOW", app_exit)
    
    my_window.geometry("%dx%d+200+20" %(window_width,window_height))

    my_window.bind("s", play_event)
    my_window.bind("p", pause_event)
    my_window.bind("r", resume_event)
    my_window.bind("q", stop_event)
    my_window.bind("l", loop_event)
    my_window.bind("n", next_event)
    
    #setup a canvas onto which will not be drawn the video!!
    canvas = Canvas(my_window, bg='black')
    canvas.config(height=canvas_height, width=canvas_width)
    canvas.grid(row=1,columnspan=2)
    
    # make sure focus is set on canvas.
    canvas.focus_set()

    display_time = tk.StringVar()
# define time/status display for selected track
    time_label = Label(canvas, font=('Comic Sans', 11),
                            fg = 'black', wraplength = 300,
                            textvariable=display_time, bg="grey")
    time_label.grid(row=0, column=0, columnspan=1)

    #track is used as a global variable in the test  harness.
    track="/home/pi/pipresents/videos/xthresh.mp4"
    break_from_loop=False
    #create a dictionary of options and create a videoplayer object
    cd={'omx-other-options' : '-t on',
            'omx-audio' : '-o hdmi'}
    vp=VideoPlayer(canvas,cd)


    my_window.mainloop()


                                            




   

